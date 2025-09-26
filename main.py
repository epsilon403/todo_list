import tkinter as tk
from tkinter import ttk
from sqlalchemy import (
    Table,
    MetaData,
    Column,
    Integer,
    String,
    Text,
    create_engine,
    select,
    insert,
    delete,
    update,
    Enum,
    text
)
from sqlalchemy.orm import sessionmaker

# Database setup
metadata = MetaData()
engine = create_engine('postgresql://postgres:epsilon2001@localhost:5432/to_do_list')
Session = sessionmaker(bind=engine)

class to_do_app:
    def __init__(self, root):
        
        self.root = root
        self.task_table = Table('tasks', metadata, autoload_with=engine)
        try:
           root.iconbitmap('icon.ico')
        except tk.TclError:
             print("Icon file 'icon.ico' not found. Using default icon.")
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

        columns = ('id', 'title', 'description', 'toggle', 'delete', 'status')
        self.task_treeview = ttk.Treeview(self.root, columns=columns, show='headings')
        self.task_treeview.heading('id', text='ID')
        self.task_treeview.heading('title', text='Title')
        self.task_treeview.heading('description', text='Description')
        self.task_treeview.heading('toggle', text='Toggle Status')
        self.task_treeview.heading('delete', text='Delete')
        self.task_treeview.heading('status', text='Status')

        self.task_treeview.column('id', width=40, anchor='center')
        self.task_treeview.column('toggle', width=100, anchor='center')
        self.task_treeview.column('delete', width=80, anchor='center')
        self.task_treeview.column('status', width=80, anchor='center')
        
        self.task_treeview.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.task_treeview.bind('<Button-1>', self.handle_click)
        
        self.show_all_tasks()

    def add_task(self):
        task = self.task_entry.get()
        description = self.description_entry.get()

        if not task:  # if add empty tasks
            return

        statement = insert(self.task_table).values(
            title=task, 
            description=description, 
            completed='undone'
        )
        
        with engine.connect() as conn:
            conn.execute(statement)
            conn.commit()

        print(f"Task added: {task}")
        
        # clear the input boxes
        self.task_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)
        
        # refresh the list
        self.show_all_tasks()

    def show_all_tasks(self):
        # clear the tree before adding new items
        for item in self.task_treeview.get_children():
            self.task_treeview.delete(item)

        with engine.connect() as conn:
            result = conn.execute(select(self.task_table))
            all_tasks = result.fetchall()
        
        if all_tasks:
            for task in all_tasks:
       
                column_names = list(self.task_table.columns.keys())
                completed_index = column_names.index('completed')

                current_status = task[completed_index]
                toggle_text = "Mark Done" if current_status == 'undone' else "Mark Undone"
                

                values_with_actions = (
                    task[0],        
                    task[1],      
                    task[2],        
                    toggle_text,   
                    "Delete",       
                    current_status  
                )
                self.task_treeview.insert('', tk.END, values=values_with_actions)
        
        print("Task list refreshed.")

    def handle_click(self, event):
        """handles clicks on action buttons."""
        region = self.task_treeview.identify("region", event.x, event.y)
        column = self.task_treeview.identify_column(event.x)

        if region == "cell":
            selected_item = self.task_treeview.focus()
            if selected_item:
                item_details = self.task_treeview.item(selected_item)
                task_id = item_details['values'][0]  
                current_status = item_details['values'][5]  
                
                print(f"Debug - Clicked column: {column}, Task ID: {task_id}, Current status: {current_status}")
                
                if column == "#4":  # change Status column
                    new_status = 'done' if current_status == 'undone' else 'undone'
                
                    self.toggle_task_status(task_id, new_status)
                    
                elif column == "#5":  # delete column
                   
                    self.delete_task(task_id)

    def toggle_task_status(self, task_id, new_status):
        """ task completion status between 'undone' and 'done'."""
        statement = update(self.task_table).where(
            self.task_table.c.id == task_id
        ).values(completed=new_status)
        
        with engine.connect() as conn:
            conn.execute(statement)
            conn.commit()
        
        self.show_all_tasks()

    def delete_task(self, task_id):
        """delelete a task from the database."""
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