from warnings import filterwarnings

# Avoid flask_sqlalchemy `time.clock` deprecationWarning
filterwarnings(
    action="ignore",
    category=DeprecationWarning,
    module="flask_sqlalchemy.__init__",
    lineno=264,
    append=True,
)
