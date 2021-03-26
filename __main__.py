import tool

try:
    tool.main()
except BrokenPipeError:
    pass # if a downstream process terminates, quit quietly
