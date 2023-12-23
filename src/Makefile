CC = gcc
CFLAGS = -Wall -Wextra -g 

# List of source files
SRCS = tide_debug.c tide_base.c

# List of object files
OBJS = $(SRCS:.c=.o)

# List of header files
HDRS = tide_base.h 

# Name of the executable
TARGET = tide_debug

# Default target
all: $(TARGET)

# Rule to build the executable
$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $@ $^ -lm

# Rule to compile source files
%.o: %.c $(HDRS)
	$(CC) $(CFLAGS) -c $< -o $@

# Clean rule
clean:
	rm -f $(OBJS) $(TARGET)