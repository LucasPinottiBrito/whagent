from app.services.agent_service import AgentService


def main() -> None:
    agent = AgentService()
    history: list[str] = []
    print("Whagent agent chat. Digite exit ou quit para sair.")
    while True:
        text = input("Voce: ").strip()
        if text.lower() in {"exit", "quit"}:
            break
        if not text:
            continue
        history.append(f"Cliente: {text}")
        result = agent.run(
            customer_input="\n".join(history),
            context={"mode": "local_ephemeral"},
        )
        history.append(f"Agente: {result.reply_text}")
        print(f"Agente: {result.reply_text}")
        print(f"Intent: {result.intent}")
        print(f"Score: {result.score}")
        print(f"Vehicle interest: {result.vehicle_interest}")
        print(f"Tools used: {', '.join(result.tools_used) if result.tools_used else '-'}")


if __name__ == "__main__":
    main()
