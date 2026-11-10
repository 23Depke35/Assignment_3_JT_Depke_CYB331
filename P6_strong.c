#include <stdio.h>
#include <ctype.h>
#include <string.h>

#define MAX_NAME_LEN 63

int main(void) {
    // Buffer size is MAX_NAME_LEN + 1 for the null terminator
    char name[MAX_NAME_LEN + 1];

    printf("Enter your name: ");

    // Use fgets instead of gets to prevent buffer overflow (CWE-120)
    if (fgets(name, sizeof(name), stdin) == NULL) {
        fprintf(stderr, "Error reading input.\n");
        return 1;
    }

    size_t len = strlen(name);

    // Check if the newline character was read; if so, strip it.
    // If not, it means the input exceeded MAX_NAME_LEN characters, 
    // so we disregard the rest of the input stream.
    if (len > 0 && name[len - 1] == '\n') {
        name[len - 1] = '\0';
    } else {
        int c;
        while ((c = getchar()) != '\n' && c != EOF) {
            // Discard remaining characters in the input buffer
        }
    }

    // Recalculate length after stripping newline
    len = strlen(name);

    // Validate that the input is not empty and contains only allowed characters:
    // letters, spaces, apostrophes, and hyphens.
    if (len == 0) {
        fprintf(stderr, "Error: Name cannot be empty.\n");
        return 1;
    }

    for (size_t i = 0; i < len; i++) {
        unsigned char c = (unsigned char)name[i];
        if (!isalpha(c) && c != ' ' && c != '\'' && c != '-') {
            fprintf(stderr, "Error: Invalid character '%c' found. Only letters, spaces, apostrophes, and hyphens are allowed.\n", c);
            return 1;
        }
    }

    // Print the greeting safely
    printf("Hello, %s!\n", name);

    return 0;
}