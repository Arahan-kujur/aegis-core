"""
Demo script for Aegis with LangChain agents.

This demo shows how Aegis intercepts risky actions from different LangChain agent types
and requires human approval when needed.
"""

import time
from typing import Any, Dict, List, Optional
from aegis.wrapper import AegisWrapper

# Try to import LangChain components
try:
    from langchain.agents import AgentExecutor, initialize_agent, AgentType
    from langchain.agents.agent import Agent
    from langchain.callbacks.base import BaseCallbackHandler
    from langchain.schema import AgentAction, AgentFinish, LLMResult
    from langchain.tools import Tool
    from langchain.llms import FakeListLLM
    from langchain.chat_models import ChatOpenAI
    from langchain.prompts import MessagesPlaceholder
    from langchain.memory import ConversationBufferMemory
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    BaseCallbackHandler = object  # Fallback base class
    Tool = Any  # Fallback type
    print("⚠️  LangChain not installed. Install with: pip install langchain openai")
    print("   Falling back to simulated demo...\n")


# Only define callback handler if it makes sense (even with fallback)
class AegisCallbackHandler(BaseCallbackHandler):
    """Callback handler that intercepts tool calls for Aegis."""
    
    def __init__(self, aegis_wrapper: AegisWrapper):
        """Initialize with an AegisWrapper instance."""
        self.aegis_wrapper = aegis_wrapper
        self.intercepted_tools = []
    
    def on_tool_start(
        self,
        serialized: Dict[str, Any],
        input_str: str,
        *,
        run_id: Any,
        parent_run_id: Optional[Any] = None,
        **kwargs: Any,
    ) -> Any:
        """Called when a tool starts running."""
        if not LANGCHAIN_AVAILABLE:
            return
        
        tool_name = serialized.get("name", "unknown")
        
        # Parse input_str to get tool arguments
        # This is a simplified parser - in production, you'd use proper JSON parsing
        tool_input = {}
        try:
            import json
            tool_input = json.loads(input_str) if input_str else {}
        except:
            # Fallback: try to extract cost if it's a spend_money tool
            if "cost" in input_str.lower():
                # Simple extraction - in production use proper parsing
                tool_input = {"input": input_str}
        
        # Intercept the tool call
        if self.aegis_wrapper._should_intercept(tool_name):
            approved = self.aegis_wrapper._intercept_tool_call(tool_name, tool_input)
            if not approved:
                raise Exception(f"Tool call {tool_name} was denied by Aegis")
        
        self.intercepted_tools.append((tool_name, tool_input))


def wrap_tool_with_aegis(tool: Any, aegis_wrapper: AegisWrapper) -> Any:
    """Wrap a LangChain tool to intercept calls with Aegis."""
    original_func = tool.func
    
    def wrapped_func(input_str: str) -> str:
        """
        Wrapped function that intercepts tool calls.
        
        LangChain tools typically receive input as a string that needs parsing.
        """
        import json
        
        # Convert input string to dict for Aegis
        tool_input = {}
        
        # Try to parse as JSON first
        try:
            parsed = json.loads(input_str)
            if isinstance(parsed, dict):
                tool_input = parsed
            else:
                # If it's a single value (like a number string), extract it
                if tool.name == "spend_money":
                    cost = float(parsed) if isinstance(parsed, (int, float)) else float(input_str)
                    tool_input = {"cost": cost, "description": f"API call via {tool.name}"}
                else:
                    tool_input = {"input": input_str}
        except (json.JSONDecodeError, ValueError):
            # Not JSON, try to extract meaningful data
            if tool.name == "spend_money":
                try:
                    cost = float(input_str.strip())
                    tool_input = {"cost": cost, "description": f"API call via {tool.name}"}
                except ValueError:
                    tool_input = {"input": input_str}
            elif tool.name == "delete_data":
                # Try to parse table and condition from string
                tool_input = {"input": input_str, "description": "Data deletion operation"}
            else:
                tool_input = {"input": input_str}
        
        # Intercept with Aegis before execution
        if aegis_wrapper._should_intercept(tool.name):
            approved = aegis_wrapper._intercept_tool_call(tool.name, tool_input)
            if not approved:
                raise Exception(f"Tool call '{tool.name}' was denied by Aegis approval system")
        
        # If approved, execute the original tool
        return original_func(input_str)
    
    # Create new tool with wrapped function
    return Tool(
        name=tool.name,
        func=wrapped_func,
        description=tool.description
    )


def create_risky_tools() -> List[Any]:
    """Create tools that trigger Aegis interception."""
    if not LANGCHAIN_AVAILABLE:
        # Return empty list or mock tools when LangChain isn't available
        return []
    
    import json
    
    def spend_money(input_str: str) -> str:
        """Spend money on an API call or service.
        
        Args:
            input_str: The amount to spend in dollars (as string or JSON)
        """
        try:
            # Try parsing as JSON first
            parsed = json.loads(input_str)
            cost = float(parsed) if isinstance(parsed, (int, float)) else float(input_str)
        except (json.JSONDecodeError, ValueError):
            # Not JSON, try direct float conversion
            cost = float(input_str.strip())
        return f"Spent ${cost:.2f} on API call"
    
    def send_email(input_str: str) -> str:
        """Send an email to a recipient.
        
        Args:
            input_str: JSON string with 'recipient' and 'subject' fields
        """
        try:
            data = json.loads(input_str)
            recipient = data.get("recipient", "unknown")
            subject = data.get("subject", "No subject")
        except json.JSONDecodeError:
            # Fallback parsing
            recipient = "unknown"
            subject = input_str
        return f"Sent email to {recipient} with subject: {subject}"
    
    def delete_data(input_str: str) -> str:
        """Delete data from a database table.
        
        Args:
            input_str: JSON string with 'table' and 'condition' fields
        """
        try:
            data = json.loads(input_str)
            table = data.get("table", "unknown")
            condition = data.get("condition", "")
        except json.JSONDecodeError:
            # Fallback parsing
            table = "unknown"
            condition = input_str
        return f"Deleted data from {table} where {condition}"
    
    def call_api(input_str: str) -> str:
        """Call an external API endpoint.
        
        Args:
            input_str: JSON string with 'endpoint' and optional 'method' fields
        """
        try:
            data = json.loads(input_str)
            endpoint = data.get("endpoint", "unknown")
            method = data.get("method", "GET")
        except json.JSONDecodeError:
            # Fallback: treat as endpoint URL
            endpoint = input_str
            method = "GET"
        return f"Called {method} {endpoint}"
    
    tools = [
        Tool(
            name="spend_money",
            func=spend_money,
            description="Spend money on an API call or service. Input should be the amount in dollars as a string."
        ),
        Tool(
            name="send_email",
            func=send_email,
            description="Send an email to a recipient. Input should be JSON with 'recipient' and 'subject' fields."
        ),
        Tool(
            name="delete_data",
            func=delete_data,
            description="Delete data from a database table. Input should be JSON with 'table' and 'condition' fields."
        ),
        Tool(
            name="call_api",
            func=call_api,
            description="Call an external API endpoint. Input should be JSON with 'endpoint' and optional 'method' fields."
        ),
    ]
    
    return tools


def create_fake_llm() -> Any:
    """Create a fake LLM for testing without API keys."""
    if LANGCHAIN_AVAILABLE:
        # Use FakeListLLM for testing
        responses = [
            "I need to spend $50 on an API call",
            "Action: spend_money\nAction Input: 50",
            "I need to spend $250 on an expensive API call",
            "Action: spend_money\nAction Input: 250",
            "I need to delete inactive users",
            "Action: delete_data\nAction Input: {\"table\": \"users\", \"condition\": \"status='inactive'\"}",
        ]
        return FakeListLLM(responses=responses)
    return None


def demo_react_agent(aegis_wrapper: AegisWrapper):
    """Demo with ReAct agent."""
    print("\n" + "=" * 70)
    print("DEMO 1: ReAct Agent (Zero-shot)")
    print("=" * 70)
    print()
    
    if not LANGCHAIN_AVAILABLE:
        print("⚠️  LangChain not available - simulating...")
        print("   Would create ReAct agent with Aegis-wrapped tools")
        return
    
    tools = create_risky_tools()
    # Wrap tools with Aegis interception
    wrapped_tools = [wrap_tool_with_aegis(tool, aegis_wrapper) for tool in tools]
    
    llm = create_fake_llm()
    
    try:
        # Create ReAct agent with wrapped tools
        agent = initialize_agent(
            tools=wrapped_tools,
            llm=llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True
        )
        
        print("Agent created: ReAct (Zero-shot)")
        print("Tools wrapped with Aegis: Yes")
        print("Cost limit: ${:.2f}".format(aegis_wrapper.cost_limit))
        print()
        
        # Test 1: Low-cost action (auto-approved)
        print("-" * 70)
        print("Test 1: Low-cost action ($50 - auto-approved)")
        print("-" * 70)
        try:
            # Manually trigger tool call for demo
            tool = wrapped_tools[0]  # spend_money
            result = tool.run("50")
            print(f"✓ Tool executed: {result}")
        except Exception as e:
            print(f"Tool execution: {str(e)}")
        
        time.sleep(1)
        
        # Test 2: High-cost action (requires approval)
        print("\n" + "-" * 70)
        print("Test 2: High-cost action ($250 - requires approval)")
        print("-" * 70)
        print("⏸  This will pause for human approval...")
        print("📋 Open the URL that appears to approve/deny")
        print()
        try:
            tool = wrapped_tools[0]  # spend_money
            result = tool.run("250")
            print(f"✓ Tool executed: {result}")
        except Exception as e:
            if "denied" in str(e).lower():
                print(f"✗ Tool call denied: {str(e)}")
            else:
                print(f"Tool execution: {str(e)}")
            
    except Exception as e:
        print(f"Error creating agent: {e}")
        print("Note: This demo requires LangChain to be installed")


def demo_conversational_agent(aegis_wrapper: AegisWrapper):
    """Demo with Conversational agent."""
    print("\n" + "=" * 70)
    print("DEMO 2: Conversational Agent")
    print("=" * 70)
    print()
    
    if not LANGCHAIN_AVAILABLE:
        print("⚠️  LangChain not available - simulating...")
        print("   Would create Conversational agent with memory")
        return
    
    tools = create_risky_tools()
    # Wrap tools with Aegis interception
    wrapped_tools = [wrap_tool_with_aegis(tool, aegis_wrapper) for tool in tools]
    
    llm = create_fake_llm()
    
    try:
        # Create conversational agent with memory
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        agent = initialize_agent(
            tools=wrapped_tools,
            llm=llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            verbose=True,
            memory=memory
        )
        
        print("Agent created: Conversational ReAct")
        print("Has memory: Yes")
        print("Tools wrapped with Aegis: Yes")
        print("Cost limit: ${:.2f}".format(aegis_wrapper.cost_limit))
        print()
        
        # Test: Data-destructive action
        print("-" * 70)
        print("Test: Data-destructive action (always requires approval)")
        print("-" * 70)
        print("⏸  This will pause for human approval...")
        print("📋 Open the URL that appears to approve/deny")
        print()
        try:
            # Manually trigger tool call for demo
            delete_tool = wrapped_tools[2]  # delete_data
            result = delete_tool.run('{"table": "users", "condition": "status=\'inactive\'"}')
            print(f"✓ Tool executed: {result}")
        except Exception as e:
            if "denied" in str(e).lower():
                print(f"✗ Tool call denied: {str(e)}")
            else:
                print(f"Tool execution: {str(e)}")
            
    except Exception as e:
        print(f"Error creating agent: {e}")


def demo_custom_agent(aegis_wrapper: AegisWrapper):
    """Demo with a custom agent wrapper."""
    print("\n" + "=" * 70)
    print("DEMO 3: Custom Agent Wrapper")
    print("=" * 70)
    print()
    
    if not LANGCHAIN_AVAILABLE:
        print("⚠️  LangChain not available - simulating...")
        print("   Would create custom agent with Aegis-wrapped tools")
        print()
        print("   This demo shows manual tool call interception:")
        print("   (Even without LangChain, Aegis can intercept tool calls)")
        print()
    
    # Create a simple custom agent that doesn't require LangChain tools
    class CustomAgent:
        """Custom agent that makes tool calls."""
        
        def __init__(self):
            self.name = "CustomAgent"
        
        def run(self, query: str):
            """Run the agent with a query."""
            # This agent just returns a message - tool calls are intercepted separately
            return f"Agent processed: {query}"
    
    agent = CustomAgent()
    
    # Wrap with Aegis
    wrapped = AegisWrapper(agent, cost_limit=aegis_wrapper.cost_limit)
    
    print("Agent created: Custom Agent")
    print("Cost limit: ${:.2f}".format(wrapped.cost_limit))
    print()
    
    # Manually intercept tool calls (simulating what would happen)
    print("-" * 70)
    print("Test: Manual tool call interception")
    print("-" * 70)
    print("(This demonstrates Aegis interception without requiring LangChain)")
    print()
    
    # Low-cost
    print("1. Low-cost action ($50 - auto-approved):")
    approved = wrapped._intercept_tool_call("spend_money", {"cost": 50.0})
    print(f"   ✓ Approved: {approved}")
    
    time.sleep(1)
    
    # High-cost
    print("\n2. High-cost action ($250 - requires approval):")
    print("   ⏸  This will pause for human approval...")
    print("   📋 Open the URL that appears to approve/deny")
    print()
    approved = wrapped._intercept_tool_call("spend_money", {"cost": 250.0})
    if approved:
        print(f"   ✓ Approved: {approved}")
    else:
        print(f"   ✗ Denied: {approved}")
    
    time.sleep(1)
    
    # Data-destructive
    print("\n3. Data-destructive action (always requires approval):")
    print("   ⏸  This will pause for human approval...")
    print("   📋 Open the URL that appears to approve/deny")
    print()
    approved = wrapped._intercept_tool_call(
        "delete_data",
        {"table": "users", "condition": "status='inactive'", "count": 150}
    )
    if approved:
        print(f"   ✓ Approved: {approved}")
    else:
        print(f"   ✗ Denied: {approved}")


def main():
    """Main demo function."""
    print("=" * 70)
    print("AEGIS DEMO - Testing with LangChain Agents")
    print("=" * 70)
    print()
    
    if not LANGCHAIN_AVAILABLE:
        print("⚠️  LangChain is not installed.")
        print("   Install with: pip install langchain")
        print("   For OpenAI agents: pip install langchain openai")
        print()
        print("   Continuing with simulated demos...")
        print()
    
    # Create Aegis wrapper (will be used by all agents)
    cost_limit = 100.0
    print(f"Setting up Aegis with cost_limit=${cost_limit:.2f}")
    print("(Actions costing more than ${:.2f} require human approval)".format(cost_limit * 2))
    print()
    
    # Create a dummy agent for the wrapper (we'll use callbacks for real agents)
    class DummyAgent:
        def run(self, input_text: str):
            return "Dummy agent"
    
    aegis_wrapper = AegisWrapper(DummyAgent(), cost_limit=cost_limit)
    
    # Run different demos
    demo_react_agent(aegis_wrapper)
    time.sleep(2)
    
    demo_conversational_agent(aegis_wrapper)
    time.sleep(2)
    
    demo_custom_agent(aegis_wrapper)
    
    # Summary
    print("\n" + "=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)
    print()
    print("📊 Check logs.jsonl to see all logged events:")
    print("   - allowed: Auto-approved actions")
    print("   - paused: Actions that required approval")
    print("   - approved: Human-approved actions")
    print("   - denied: Human-denied actions")
    print()
    print("💡 Tips:")
    print("   - Install langchain: pip install langchain")
    print("   - For OpenAI agents: pip install langchain openai")
    print("   - Set OPENAI_API_KEY environment variable for real agents")
    print("   - This demo uses FakeListLLM for testing (no API keys needed)")
    print()
    print("📝 Note:")
    print("   The demo wraps tools with Aegis to intercept tool calls.")
    print("   In production, you can also use callbacks or wrap the agent executor.")
    print()


if __name__ == "__main__":
    main()
