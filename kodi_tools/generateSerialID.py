# The ID field of JSONRPC commands is designed to combat race conditions.
# Commands without a delay need this to sequence correctly

# Nonlocal declaration not allowed at module level;
# syntax gotcha requires this abstraction
def gen_counter(init=1):
    count = init
    def counter():
        nonlocal count
        count += 1
        return count
    return counter

get_id = gen_counter()