# Boolean_Logic_Synthesis_Engine
This is a program for optimizing Boolean expressions or digital circuits. It can optimize the input file describing any Boolean expression or digital circuit and output the optimal result (including but not limited to SOP, POS, inversion, prime implication, essential prime implication)


## Guidance for Using the Code

This code is an interactive user program designed to accept a filename from the user and process the file content based on user selection. Here’s how to use this code:

### 1. **Enter the Filename**
   - The program will first prompt you to enter a filename. This should be a file containing boolean equations or circuit descriptions.

### 2. **Select the Input Type**
   - The program will ask you to choose the type of input. You can select:
     - Circuit (C)
     - Boolean equation (B)

### 3. **Enter the Export Filename**
   - The program will prompt you to enter the name for the export file. The processed results will be saved in this file.

### If Boolean Equation (B) is Selected:

- The program will read the file containing boolean equations and convert them into a specific format.
- It will display the converted boolean equations.
- The processed boolean equations will be exported to the output file you specified earlier.

### If Circuit (C) is Selected:

- The program will construct a boolean expression corresponding to the circuit described in the file.
- It will display the corresponding boolean equation.

### Error Handling:

- If the entered filename does not exist, the program will display an error message.

### Example:

- First, the program will prompt you to enter the filename, where you could enter something like `input.txt`.
- Next, it will ask you to choose the type of input. You can enter `B` (Boolean Equation) or `C` (Circuit).
- Then, it will ask you to enter the name for the export file, like `output.txt`.
- Finally, it will display the processed boolean equations and save them in the `output.txt` file.

Ensure your input file is correctly formatted and contains content that aligns with the program's requirements, and enter information accurately as prompted.
##  Input
### Boolean Equations

### Circuit Descrption Language
This Circuit Descrption Language describes a Boolean function composed of a sequence of Boolean operations with NOT, AND, and OR only. Each line in the code represents a Boolean operation, following specific conventions:

#### 1. **NOT Operation**
   ```plaintext
   not (output, input)
   ```
   - The NOT operation takes one input and produces one output, performing a logical negation on the input.

#### 2. **AND Operation**
   ```plaintext
   and (output, input1, input2)
   ```
   - The AND operation takes two inputs and produces one output, performing a logical AND operation between the two inputs.

#### 3. **OR Operation**
   ```plaintext
   or (output, input1, input2)
   ```
   - The OR operation takes two inputs and produces one output, performing a logical OR operation between the two inputs.

#### 4. **OUT Operation**
   ```plaintext
   out (output)
   ```
   - The OUT operation specifies the final output of the Boolean function.

#### Detailed Description

- Each operation is identified with a unique output variable such as `notC`, `and0`, `or2`, etc.
- Inputs to operations can be outputs of preceding operations or original Boolean variables like `A`, `B`, `C`, etc.
- The code is executed sequentially from top to bottom, where each operation is performed based on previous results.
- The `out` operation indicates the overall output of the Boolean function.

#### Examples

- `not (notC, C)` : NOT operation negating `C` and storing the result in `notC`.
- `and (and0, notC, B)` : AND operation between `notC` and `B`, storing the result in `and0`.
- `or (or2, or0, or1)` : OR operation between `or0` and `or1`, storing the result in `or2`.
- `out (or2)` : Specifying `or2` as the final output      **MUST EXIST IN CIRCUIT!**         
