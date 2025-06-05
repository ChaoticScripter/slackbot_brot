#==========================
# app/handlers/homeMenu.py
#==========================

def create_home_view():
    return {
        "type": "home",
	"blocks": [
		{
			"type": "rich_text",
			"elements": [
				{
					"type": "rich_text_section",
					"elements": [
						{
							"type": "text",
							"text": "Hallo ",
							"style": {
								"bold": True
							}
						},
						{
							"type": "user",
							"user_id": user_id,
							"style": {
								"bold": True
							}
						},
						{
							"type": "text",
							"text": "!\nWillkommen beim Brotbot! ",
							"style": {
								"bold": True
							}
						},
						{
							"type": "emoji",
							"name": "bread",
							"unicode": "1f35e",
							"style": {
								"bold": True
							}
						}
					]
				}
			]
		},
		{
			"type": "divider"
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "*Verfügbare Befehle:*\n\n• `/order add <Produkt> <Menge>` - Neue Bestellung aufgeben\n• `/order list` - Aktuelle Bestellungen anzeigen\n• `/name` - Namen anzeigen/ändern\n• `/help` - Hilfe anzeigen"
			}
		},
		{
			"type": "context",
			"elements": [
				{
					"type": "mrkdwn",
					"text": "🕐 Bestellungen werden jeden Mittwoch um 10:00 Uhr gesammelt"
				}
			]
		},
		{
			"type": "divider"
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "🚧 WIP! 🚧 ~Schnellzugriff auf Funktionen:~ 🚧 SOON! 🚧"
			}
		},
		{
			"type": "actions",
			"elements": [
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "🛒 Neue Bestellung",
						"emoji": True
					},
					"action_id": "new_order_clicked",
					"style": "danger"
				},
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "📋 Meine Bestellungen",
						"emoji": True
					},
					"action_id": "my_orders_clicked",
					"style": "danger"
				}
			]
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "🚧 WIP! 🚧 ~Schnellzugriff auf Funktionen:~ 🚧 SOON! 🚧"
			}
		},
		{
			"type": "divider"
		}
	]
}

def handle_app_home_opened(client, event, logger):
    try:
        client.views_publish(
            user_id=event["user"],
            view=create_home_view()
        )
    except Exception as e:
        logger.error(f"Error publishing home view: {e}")