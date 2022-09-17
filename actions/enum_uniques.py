from enum import Enum


class Id(Enum):
    # To differentiate between Telegram and Android app
    ANDROID_UUID_LENGTH = 53
    TELEGRAM_UUID_LENGTH = 16

    # Number of subjects to display in plot
    PLOT_GRAPH_NUM_OF_SUBJECTS = 5

    # Suggest topic as to be improved, if user scores below this ratio
    IMPROVEMENT_SUGGESTION_RATIO = 0.7

    # Number of subjects and topics to display as button
    SUBJECT_BUTTONS = 6
    TOPIC_BUTTONS = 5

    # Language code
    EN = English = 'English'
    DE = German = 'Deutsch'
    EL = Greek = 'Ελληνική'
    ES = Spanish = 'Español'
