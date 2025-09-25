from tkinter import *
from tkinter import ttk
import tkinter as tk
from sqlalchemy.orm import Session
from sqlalchemy import Table , MetaData , create_engine , insert , select , text , delete

metadata = MetaData()
engine = create_engine('postgresql://postgres:epsilon2001@localhost:5432/to_do_list')


# def on_entry_click(event):
#     """Function to be called when the entry is clicked."""
#     if entry2.get() == 'Enter the description':
#        entry2.delete(0, "end") # delete all the text in the entry
#        entry2.insert(0, '') # Insert blank for user input
#        entry2.config(fg='black') # Change text color to black

# def on_focusout(event):
#     """Function to be called when the entry loses focus."""
#     if entry2.get() == '':
#         entry2.insert(0, 'Enter the description')
#         entry2.config(fg='grey')


# window = tk.Tk()
# greeting = tk.Label(text = 'hello to my todo list' , width=100 , height=100)
# entry1 = tk.Entry(window , text = 'enter the task title' , background="red")
# entry2 = tk.Entry(window, width=20, fg='grey')
# entry2.pack(pady=15)
# entry2.insert(0, 'Enter the description')
# entry1.insert(0 , 'enter votre prenom')

# # Bind the functions to the widget's events
# entry2.bind('<FocusIn>', on_entry_click)
# entry2.bind('<FocusOut>', on_focusout)
# entry2.pack(pady=15)
# select_prioriy = ttk.Combobox(window , values=["green" , "orange" , "red"])




# select_prioriy.pack(pady=15)
# entry1.pack(pady=15)
# greeting.pack(pady=15)
# window.mainloop()$



class to_do_app:
    def __init__(self, root):
        self.root = root
        self.task_table = Table('tasks', metadata, autoload_with=engine)

        self.root.title('To-Do List')
        self.session = Session()
        self.main_frame = ttk.Frame(self.root, padding=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(self.main_frame, text="New Task:").grid(row=0, column=0, sticky="w", pady=5)
        self.task_entry = ttk.Entry(self.main_frame, width=40)
        self.task_entry.grid(row=0, column=1, sticky="ew", padx=5)

        ttk.Label(self.main_frame, text="Description:").grid(row=1, column=0, sticky="w", pady=5)
        self.description_entry = ttk.Entry(self.main_frame, width=40)
        self.description_entry.grid(row=1, column=1, sticky="ew", padx=5)

        self.button = tk.Button(self.main_frame, text="Add Task", command=self.add_task, font=('arial', 12))
        self.button.grid(row=2, column=1, sticky="w", padx=5, pady=10)

        self.show_button = tk.Button(self.main_frame, text='Refresh List', command=self.show_all_tasks, font=('arial', 12))
        self.show_button.grid(row=2, column=1, sticky="e", padx=5, pady=10)


        columns = ('id', 'title', 'description', 'action')
        self.task_treeview = ttk.Treeview(self.root, columns=columns, show='headings')
        self.task_treeview.heading('id', text='ID')
        self.task_treeview.heading('title', text='Title')
        self.task_treeview.heading('description', text='Description')
        self.task_treeview.heading('action', text='Action')

        self.task_treeview.column('id', width=40, anchor='center')
        self.task_treeview.column('action', width=100, anchor='center')
        
        self.task_treeview.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)


        self.task_treeview.bind('<Button-1>', self.handle_click)
        

        self.show_all_tasks()



        
        
    def add_task(self):
        task = self.task_entry.get()
        description = self.description_entry.get()

        if not task: # Don't add empty tasks
            return

        statement = insert(self.task_table).values(title=task, description=description)
        
        with engine.connect() as conn:
            conn.execute(statement)
            conn.commit() # Make sure to commit the changes

        print(f"Task added: {task}")
        
        # Clear the input boxes
        self.task_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)
        
        # Refresh the list to show the new task
        self.show_all_tasks()

    def show_all_tasks(self):
        # Clear the tree before adding new items
        for item in self.task_treeview.get_children():
            self.task_treeview.delete(item)

        with engine.connect() as conn:
            result = conn.execute(select(self.task_table))
            all_tasks = result.fetchall()
        
        if all_tasks:
            for task in all_tasks:
                # --- THIS IS THE KEY CHANGE ---
                # Add the word "Delete" to the values tuple for the 'action' column
                values_with_action = (task[0], task[1], task[2], "Delete")
                self.task_treeview.insert('', tk.END, values=values_with_action)
        
        print("Task list refreshed.")

    def handle_click(self, event):
        """Checks if a click happened on a 'Delete' cell."""
        region = self.task_treeview.identify("region", event.x, event.y)
        column = self.task_treeview.identify_column(event.x)

        # Column #4 is our 'action' column
        if region == "cell" and column == "#4":
            selected_item = self.task_treeview.focus()
            if selected_item:
                item_details = self.task_treeview.item(selected_item)
                task_id = item_details['values'][0] # The ID is the first value
                self.delete_task(task_id)

    def delete_task(self, task_id):
  
        statement = delete(self.task_table).where(self.task_table.c.id == task_id) 
        with engine.connect() as conn:
            conn.execute(statement)
            conn.commit() 
        
        print(f"The task with the id: {task_id} is deleted")
        

        self.show_all_tasks()

if __name__ == '__main__':
    root = tk.Tk()
    app = to_do_app(root)
    root.mainloop()
