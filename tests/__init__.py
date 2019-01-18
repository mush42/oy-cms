from warnings import filterwarnings

# Avoid flask_sqlalchemy `time.clock` deprecationWarning on windows
filterwarnings(
    action="ignore",
    category=DeprecationWarning,
    module="flask_sqlalchemy",
    append=True,
)
