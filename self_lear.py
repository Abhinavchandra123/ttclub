import psycopg2
import csv

class QADatabase:
    def __init__(self, dbname, user, password, host="localhost", port="5432"):
        self.conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        self.cursor = self.conn.cursor()

    def create_table(self):
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS qa_table (
            id SERIAL PRIMARY KEY,
            question TEXT UNIQUE,
            answer TEXT
        )
        '''
        self.cursor.execute(create_table_query)
        self.conn.commit()

    # def get_answer(self, question):
    #     select_query = "SELECT answer FROM qa_table WHERE question = %s"
    #     self.cursor.execute(select_query, (question,))
    #     result = self.cursor.fetchone()
    #     if result:
    #         return result[0]
    #     else:
    #         return None
    def get_answer(self, question):
        words = question.split()  # Split the question into words
        max_matched_words = 0
        matched_answer = None

        select_query = "SELECT question, answer FROM qa_table"
        self.cursor.execute(select_query)
        rows = self.cursor.fetchall()

        for row in rows:
            db_question = row[0]
            db_answer = row[1]
            db_words = db_question.split()  # Split the database question into words

            # Find the number of matching words between the question and database question
            matched_words = sum(1 for word in words if word in db_words)

            if matched_words > max_matched_words:
                max_matched_words = matched_words
                matched_answer = db_answer

        return matched_answer
    
    def delete_all_data(self):
        try:
            delete_query = "DELETE FROM qa_table"
            self.cursor.execute(delete_query)
            self.conn.commit()
            print("All data deleted successfully.")
        except Exception as e:
            print("An error occurred while deleting data:", e)


    def save_to_csv(self, filename="question_ans.csv"):
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Question', 'Answer'])
                select_query = "SELECT question, answer FROM qa_table"
                self.cursor.execute(select_query)
                rows = self.cursor.fetchall()
                for row in rows:
                    writer.writerow(row)
            print(f"Data saved to {filename} successfully.")
        except Exception as e:
            print("An error occurred while saving data to CSV:", e)

    def add_qa_pair(self, question, answer):
        insert_query = "INSERT INTO qa_table (question, answer) VALUES (%s, %s)"
        self.cursor.execute(insert_query, (question, answer))
        self.conn.commit()

    def close_connection(self):
        self.cursor.close()
        self.conn.close()

# Function to insert knowledge from a CSV file
def insert_from_csv(db):
    csv_file = input("Enter the path to the CSV file: ")
    try:
        with open(csv_file, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row_number, row in enumerate(reader, start=1):
                try:
                    question = row['Questions'].strip('"')
                    correct_answer = row['Correct']
                    db.add_qa_pair(question, correct_answer)
                    print(f"Row {row_number}: Question '{question}' inserted successfully.")
                except KeyError as ke:
                    print(f"Row {row_number}: Missing required key in CSV row: {ke}")
                except psycopg2.IntegrityError as ie:
                    if ie.pgcode == '23505':  # Check if the error code is for duplicate key violation
                        print(f"Row {row_number}: The question '{question}' already exists in the database. Skipping...")
                    else:
                        print(f"Row {row_number}: An error occurred while processing row: {ie}")
                except Exception as e:
                    print(f"Row {row_number}: An error occurred while processing row: {e}")
        print("All questions and answers inserted successfully.")
    except FileNotFoundError:
        print("File not found.")
    except Exception as e:
        print("An error occurred:", e)


def main():
    dbname = "qa_database"
    user = "postgres"
    password = "1708580"
    db = QADatabase(dbname, user, password)
    db.create_table()

    while True:
        print("Options:")
        print("1. Ask a question")
        print("2. Insert knowledge from a CSV file")
        print("3. Print out all question and answers")
        print("4. Delete all data from the table")
        print("5. Quit")
        option = input("Enter option number: ")

        if option == '1':
            question = input("Ask a question (type 'quit' to exit): ")
            answer = db.get_answer(question)
            if answer:
                print("Answer:", answer)
            else:
                new_answer = input("I don't know the answer. Please provide it: ")
                db.add_qa_pair(question, new_answer)
                print("Thank you! I've learned something new.")
            
        elif option == '2':
            insert_from_csv(db)
            
        elif option == '3':
            db.save_to_csv()
            
        elif option == '4':
            # Delete all data from the table
            db.delete_all_data()
            
        elif option == '5':
            # Quit
            break
        
        
        else:
            print("Invalid option. Please try again.")

    db.close_connection()

if __name__ == "__main__":
    main()
