// Author: Jack Lidster
// Date: 01-26-2026
// Description: Calculator that accepts any integer numbers.

import java.util.Scanner;
import java.util.Arrays;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class NeedlesslyComplexOneDigitCalc {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        // Information Logic - I didn't want to do print statements..
        String[] info = {
            " ",
            "Hello and welcome to this calculator! :D",
            " ",
            "1. This program accepts any integer calculations.",
            "2. You can use positive or negative integers of any size.",
            "3. It allows these mathematical operators: ",
            " ",
            "[+] Addition, [-] Subtraction, [*] Multiplication & [/] Division.",
            " ",
            "Example formats: 5+3, 100*25, -50+30, 1000/4",
            " "
        };

        for (String item : info) {
            System.out.println(item);
        }

        // Error Messages
        String notValidEquation = "Please enter a valid equation (e.g., 5+3, 100*25, -10+5).";
        String notValidOperator = "Please enter a valid operator (+, -, *, /).";
        String canNotDivideByZero = "You cannot divide by zero.";

        // Valid Operators
        List<Character> validOperators = Arrays.asList('+', '-', '*', '/');

        // User Input
        System.out.print("Please enter your equation here: ");
        String userInput = scanner.nextLine().trim();

        // Easter egg check
        if (userInput.equals("\uD83D\uDC2B/2")) {
            System.out.println("\uD83D\uDC2B / 2 = \uD83D\uDC2A");
            System.out.print("Press 'Enter' to leave this camel. (you won't) ");
            scanner.nextLine();
            scanner.close();
            return;
        }

        // Regex pattern to match: optional negative number, operator, optional negative number
        // Pattern: (-?\d+)\s*([+\-*/])\s*(-?\d+)
        Pattern pattern = Pattern.compile("(-?\\d+)\\s*([+\\-*/])\\s*(-?\\d+)");
        Matcher matcher = pattern.matcher(userInput);

        if (!matcher.matches()) {
            System.out.println(notValidEquation);
            System.out.print("Press 'Enter' to end this program. :D ");
            scanner.nextLine();
            scanner.close();
            return;
        }

        // Extract the numbers and operator
        long firstNumber;
        long secondNumber;
        char operator;

        try {
            firstNumber = Long.parseLong(matcher.group(1));
            operator = matcher.group(2).charAt(0);
            secondNumber = Long.parseLong(matcher.group(3));
        } catch (NumberFormatException e) {
            System.out.println(notValidEquation);
            System.out.print("Press 'Enter' to end this program. :D ");
            scanner.nextLine();
            scanner.close();
            return;
        }

        // Validate operator
        if (!validOperators.contains(operator)) {
            System.out.println(notValidOperator);
            System.out.print("Press 'Enter' to end this program. :D ");
            scanner.nextLine();
            scanner.close();
            return;
        }

        // Math logic
        if (operator == '+') {
            System.out.println(firstNumber + " + " + secondNumber + " = " + (firstNumber + secondNumber));
        }
        if (operator == '-') {
            System.out.println(firstNumber + " - " + secondNumber + " = " + (firstNumber - secondNumber));
        }
        if (operator == '*') {
            System.out.println(firstNumber + " * " + secondNumber + " = " + (firstNumber * secondNumber));
        }
        if (operator == '/') {
            if (secondNumber == 0) {
                System.out.println(canNotDivideByZero);
            } else {
                System.out.println(firstNumber + " / " + secondNumber + " = " + ((double) firstNumber / secondNumber));
            }
        }

        System.out.print("Press 'Enter' to end this program. :D ");
        scanner.nextLine();
        scanner.close();
    }
}
