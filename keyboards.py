from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

select_metric_callback = CallbackData("select_metric", "id", "action")
rate_metric_callback = CallbackData("rate_metric", "id", "rating")

def select_metric(metrics):
    print("compiling metrics")

    keyboard = InlineKeyboardMarkup(
        row_width=1
    )

    for metric in metrics:
        print("From metric " + str(metric.id) + ": " + metric.name)
        keyboard.insert(
            InlineKeyboardButton(
                text=metric.name,
                callback_data=select_metric_callback.new(
                    id=metric.id,
                    action="none"
                )
            )
        )

    keyboard.insert(
            InlineKeyboardButton(
                text="Отменить",
                callback_data=select_metric_callback.new(id = "none", action = "cancel")
            )
    )

    print("KB: " + str(keyboard))

    return keyboard

def rate_metric(metric):
    print("compiling metric")

    keyboard = InlineKeyboardMarkup(
        row_width=5
    )

    for i in range(1, 6):
        print("From metric " + str(metric.id) + ": " + metric.name)
        keyboard.insert(
            InlineKeyboardButton(
                text=str(i),
                callback_data=rate_metric_callback.new(
                    id=metric.id,
                    rating=i
                )
            )
        )

    print("KB: " + str(keyboard))

    return keyboard