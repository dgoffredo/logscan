import tool

try:
    tool.main()
# If a downstream process terminates, or if the user enters ctrl+c on
# their terminal, then quit quitely.
except BrokenPipeError:
    pass
except KeyboardInterrupt:
    pass
