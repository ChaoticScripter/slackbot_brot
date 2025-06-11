# new/app/bot.py
from slack_bolt import App
from config.settings import settings
from app.handlers.order.handlers import OrderHandler
from app.handlers.user.handlers import UserHandler
from app.handlers.admin.handlers import AdminHandler

app = App(
    token=settings.SLACK.BOT_TOKEN,
    signing_secret=settings.SLACK.SIGNING_SECRET
)

# Order Handler initialisieren
order_handler = OrderHandler()
user_handler = UserHandler()
admin_handler = AdminHandler()

# Command Handler registrieren
app.command("/order")(order_handler.handle_order_add)
app.command("/name")(user_handler.handle_name_command)
app.command("/admin")(admin_handler.handle_admin_command)