def notificar(titulo: str, mensagem: str) -> None:
    try:
        from plyer import notification
        notification.notify(
            title=titulo,
            message=mensagem,
            app_name="AutoHub Pro",
            timeout=5,
        )
    except Exception:
        pass
