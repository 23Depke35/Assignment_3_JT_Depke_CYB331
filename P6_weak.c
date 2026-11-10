#include <stdio.h>
#include <string.h>

int main() {
    char name[100];

    // Prompt the user for their name
    printf("Enter your name: ");

    // Read the input safely, allowing spaces in the name
    if (fgets(name, sizeof(name), stdin) != NULL) {
        // Remove the trailing newline character added by fgets
        name[strcspn(name, "\n")] = '\0';

        // Print the greeting
        printf("Hello, %s! Welcome to C programming.\n", name);
    }

    return 0;
}