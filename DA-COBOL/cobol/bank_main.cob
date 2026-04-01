       IDENTIFICATION DIVISION.
       PROGRAM-ID. BANKMAIN.

       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT TXN-FILE ASSIGN TO "data/transactions.csv"
               ORGANIZATION IS LINE SEQUENTIAL
               FILE STATUS IS WS-FILE-STATUS.

       DATA DIVISION.
       FILE SECTION.
       FD  TXN-FILE.
       01  TXN-RECORD                 PIC X(400).

       WORKING-STORAGE SECTION.
       01  WS-FILE-STATUS             PIC XX.
       01  WS-ACCOUNT-ID              PIC X(10) VALUE "A1001".
       01  WS-CLIENT-NAME             PIC X(30) VALUE "John Carter".
       01  WS-BALANCE                 PIC S9(7)V99 VALUE 1000.00.
       01  WS-AMOUNT                  PIC 9(7)V99 VALUE 0.
       01  WS-TXN-TYPE                PIC X(12) VALUE SPACES.
       01  WS-TXN-ID                  PIC 9(4) VALUE 0.
       01  WS-DATE                    PIC X(10) VALUE "2026-03-31".

       01  WS-AMOUNT-DISPLAY          PIC Z(7).99.
       01  WS-BALANCE-DISPLAY         PIC -Z(7).99.
       01  WS-MERCHANT                 PIC X(24) VALUE SPACES.
       01  WS-CATEGORY                 PIC X(16) VALUE SPACES.

       01  WS-CSV-LINE.
           05  F-TXN-ID               PIC 9(4).
           05  FILLER                 PIC X VALUE ",".
           05  F-ACCOUNT-ID           PIC X(10).
           05  FILLER                 PIC X VALUE ",".
           05  F-DATE                 PIC X(10).
           05  FILLER                 PIC X VALUE ",".
           05  F-TXN-TYPE             PIC X(12).
           05  FILLER                 PIC X VALUE ",".
           05  F-AMOUNT               PIC Z(7).99.
           05  FILLER                 PIC X VALUE ",".
           05  F-BALANCE-AFTER        PIC -Z(7).99.
           05  FILLER                 PIC X VALUE ",".
           05  F-MERCHANT             PIC X(24).
           05  FILLER                 PIC X VALUE ",".
           05  F-CATEGORY             PIC X(16).

       PROCEDURE DIVISION.
       MAIN-PARA.
           PERFORM OPEN-TXN-FILE

           MOVE "Client: " TO TXN-RECORD
           DISPLAY "Starting account simulation..."
           DISPLAY "Account ID : " WS-ACCOUNT-ID
           DISPLAY "Client     : " WS-CLIENT-NAME
           MOVE WS-BALANCE TO WS-BALANCE-DISPLAY
           DISPLAY "Open Bal   : " WS-BALANCE-DISPLAY

           PERFORM POST-DEPOSIT
           PERFORM POST-PURCHASE1
           PERFORM POST-WITHDRAWAL
           PERFORM POST-PURCHASE2

           CLOSE TXN-FILE
           DISPLAY "Simulation complete."
           STOP RUN.

       OPEN-TXN-FILE.
           OPEN INPUT TXN-FILE
           IF WS-FILE-STATUS = "00"
               CLOSE TXN-FILE
               OPEN EXTEND TXN-FILE
           ELSE
               OPEN OUTPUT TXN-FILE
           END-IF
           EXIT.

       POST-DEPOSIT.
           ADD 1 TO WS-TXN-ID
           MOVE "DEPOSIT" TO WS-TXN-TYPE
           MOVE "Bank of Lies" TO WS-MERCHANT
           MOVE "Deposit" TO WS-CATEGORY
           MOVE 500.00 TO WS-AMOUNT
           ADD WS-AMOUNT TO WS-BALANCE
           PERFORM WRITE-TXN-RECORD
           EXIT.

       POST-PURCHASE1.
           ADD 1 TO WS-TXN-ID
           MOVE "PURCHASE" TO WS-TXN-TYPE
           MOVE "Toxicmart" TO WS-MERCHANT
           MOVE "Groceries" TO WS-CATEGORY
           MOVE 120.50 TO WS-AMOUNT
           SUBTRACT WS-AMOUNT FROM WS-BALANCE
           PERFORM WRITE-TXN-RECORD
           EXIT.

       POST-WITHDRAWAL.
           ADD 1 TO WS-TXN-ID
           MOVE "WITHDRAWAL" TO WS-TXN-TYPE
           MOVE "Bank of Lies" TO WS-MERCHANT
           MOve "Withdrawal" TO WS-CATEGORY
           MOVE 200.00 TO WS-AMOUNT
           SUBTRACT WS-AMOUNT FROM WS-BALANCE
           PERFORM WRITE-TXN-RECORD
           EXIT.

       POST-PURCHASE2.
           ADD 1 TO WS-TXN-ID
           MOVE "PURCHASE" TO WS-TXN-TYPE
           MOVE "Amazoni" TO WS-MERCHANT
           MOVE "BadDeals" TO WS-CATEGORY
           MOVE 164.50 TO WS-AMOUNT
           SUBTRACT WS-AMOUNT FROM WS-BALANCE
           PERFORM WRITE-TXN-RECORD
           EXIT.

       WRITE-TXN-RECORD.
           MOVE WS-TXN-ID TO F-TXN-ID
           MOVE WS-ACCOUNT-ID TO F-ACCOUNT-ID
           MOVE WS-DATE TO F-DATE
           MOVE WS-TXN-TYPE TO F-TXN-TYPE
           MOVE WS-AMOUNT TO F-AMOUNT
           MOVE WS-BALANCE TO F-BALANCE-AFTER
           MOVE WS-MERCHANT TO F-MERCHANT
           MOVE WS-CATEGORY TO F-CATEGORY
           MOVE WS-CSV-LINE TO TXN-RECORD
           WRITE TXN-RECORD

           MOVE WS-AMOUNT TO WS-AMOUNT-DISPLAY
           MOVE WS-BALANCE TO WS-BALANCE-DISPLAY
           DISPLAY "Txn " WS-TXN-ID " " WS-TXN-TYPE
                   " Amount: " WS-AMOUNT-DISPLAY
                   " Balance: " WS-BALANCE-DISPLAY
           EXIT.
           