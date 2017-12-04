import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, TIMESTAMP
from datetime import datetime

engine = create_engine("sqlite:///contacts.db", echo=True)
Base = declarative_base()


class Contact(Base):
    __tablename__ = 'contacts'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    surname = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False)
    phone_number = Column(String(15), nullable=False, unique=True)
    last_called = Column(TIMESTAMP, nullable=True)
    last_seen = Column(TIMESTAMP, nullable=True)

    def __repr__(self):
        return "<Contact(id='%s', name='%s', surname='%s', email='%s', phone_number='%s' , last_called='%s')>" % (
            self.id, self.name, self.surname, self.email, self.phone_number, self.last_called)


class ContactDialog(Gtk.Dialog):
    def __init__(self, parent, contact, see):
        Gtk.Dialog.__init__(self, "My Dialog", parent, 0,
                            (Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.set_default_size(200, 300)

        self.grid = Gtk.Grid()

        self.contact = contact

        label = Gtk.Label("Create new contact")
        name_label = Gtk.Label(label='Name')
        self.name_entry = Gtk.Entry()
        surname_label = Gtk.Label(label='Surname')
        self.surname_entry = Gtk.Entry()
        email_label = Gtk.Label(label='Email')
        self.email_entry = Gtk.Entry()
        phone_label = Gtk.Label(label='Phone')
        self.phone_entry = Gtk.Entry()

        if self.contact is not None:
            self.name_entry.set_text(contact.name)
            self.surname_entry.set_text(contact.surname)
            self.email_entry.set_text(contact.email)
            self.phone_entry.set_text(contact.phone_number)

        self.grid.attach(name_label, 0, 0, 1, 1)
        self.grid.attach_next_to(self.name_entry, name_label, Gtk.PositionType.RIGHT, 1, 1)
        self.grid.attach_next_to(surname_label, name_label, Gtk.PositionType.BOTTOM, 1, 1)
        self.grid.attach_next_to(self.surname_entry, surname_label, Gtk.PositionType.RIGHT, 1, 1)
        self.grid.attach_next_to(email_label, surname_label, Gtk.PositionType.BOTTOM, 1, 1)
        self.grid.attach_next_to(self.email_entry, email_label, Gtk.PositionType.RIGHT, 1, 1)
        self.grid.attach_next_to(phone_label, email_label, Gtk.PositionType.BOTTOM, 1, 1)
        self.grid.attach_next_to(self.phone_entry, phone_label, Gtk.PositionType.RIGHT, 1, 1)

        if see:
            self.name_entry.set_editable(False)
            self.surname_entry.set_editable(False)
            self.email_entry.set_editable(False)
            self.phone_entry.set_editable(False)
            last_seen_label = Gtk.Label(label='Last Seen: ' + str(contact.last_seen))
            self.grid.attach_next_to(last_seen_label, phone_label, Gtk.PositionType.BOTTOM, 1, 1)

        box = self.get_content_area()
        box.add(label)
        box.add(self.grid)

        self.show_all()

    def create_contact(self):
        c = Contact()
        c.name = self.name_entry.get_text()
        c.surname = self.surname_entry.get_text()
        c.email = self.email_entry.get_text()
        c.phone_number = self.phone_entry.get_text()

        return c

    def update_contact(self):
        self.contact.name = self.name_entry.get_text()
        self.contact.surname = self.surname_entry.get_text()
        self.contact.email = self.email_entry.get_text()
        self.contact.phone_number = self.phone_entry.get_text()


class Window(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title='Contacts')
        self.set_border_width(10)
        self.set_size_request(800, 600)
        self.set_resizable(False)

        # Set up self.box
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.box.set_border_width(10)
        self.filter_entry = Gtk.Entry()
        self.filter_entry.connect('activate', self.on_filter_text, self.filter_entry)
        self.box.pack_start(self.filter_entry, True, True, 0)
        self.add_button = Gtk.Button(label='Add contact')
        self.add_button.connect('clicked', self.on_add_button)
        self.box.pack_start(self.add_button, True, True, 0)
        self.update_button = Gtk.Button(label='Update contact')
        self.update_button.connect('clicked', self.on_update_button)
        self.box.pack_start(self.update_button, True, True, 0)
        self.delete_button = Gtk.Button(label='Remove contact')
        self.delete_button.connect('clicked', self.on_delete_button)
        self.box.pack_start(self.delete_button, True, True, 0)
        self.call_button = Gtk.Button(label='Call')
        self.call_button.connect('clicked', self.on_call_button)
        self.box.pack_start(self.call_button, True, True, 0)
        self.see_button = Gtk.Button(label='See contact')
        self.see_button.connect('clicked', self.on_see_button)
        self.box.pack_start(self.see_button, True, True, 0)

        # Set up the self.grid
        self.grid = Gtk.Grid()
        self.grid.set_column_homogeneous(True)
        self.grid.set_row_homogeneous(True)
        self.add(self.grid)

        # Init store for tree view
        self.contacts_liststore = Gtk.ListStore(str, str, str, str, str, str)
        self.populate_model()

        # Init filter
        self.current_filter_contacts = None
        self.contacts_filter = self.contacts_liststore.filter_new()
        self.contacts_filter.set_visible_func(self.contacts_filter_func)

        # Init tree view
        self.contacts_treeview = Gtk.TreeView.new_with_model(self.contacts_filter)
        for i, column_title in enumerate(["Name", "Surname", "Email", "Phone Number", "Last Called", "Last Seen"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            self.contacts_treeview.append_column(column)

        self.selected_contact = None
        self.contact = None
        select = self.contacts_treeview.get_selection()
        select.connect("changed", self.on_tree_selection_changed)

        # Set up layout
        self.grid.attach(self.box, 0, 0, 1, 1)
        self.scrollable_treelist = Gtk.ScrolledWindow()
        self.scrollable_treelist.set_vexpand(True)
        self.grid.attach_next_to(self.scrollable_treelist, self.box, Gtk.PositionType.RIGHT, 5, 3)
        self.scrollable_treelist.add(self.contacts_treeview)

        self.show_all()

    def contacts_filter_func(self, model, iter, data):
        if self.current_filter_contacts is None or self.current_filter_contacts == "None":
            return True
        else:
            return self.current_filter_contacts in model[iter][1]

    def on_filter_text(self, widget, entry):
        text = entry.get_text()
        self.current_filter_contacts = text if text != '' else None
        self.contacts_filter.refilter()

    def on_tree_selection_changed(self, selection):
        model, treeiter = selection.get_selected()
        if treeiter is not None:
            self.selected_contact = model[treeiter][3]

    def on_add_button(self, button):
        dialog = ContactDialog(self, None, False)
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            session.add(dialog.create_contact())
            session.commit()
            self.populate_model()
        self.contact = None
        self.selected_contact = None
        dialog.destroy()

    def on_update_button(self, button):
        if self.selected_contact is not None:
            self.contact = session.query(Contact).filter_by(phone_number=self.selected_contact).first()
            dialog = ContactDialog(self, self.contact, False)
            response = dialog.run()

            if response == Gtk.ResponseType.OK:
                dialog.update_contact()
                session.commit()
                self.populate_model()
            self.contact = None
            self.selected_contact = None
            dialog.destroy()

    def on_delete_button(self, button):
        if self.selected_contact is not None:
            self.contact = session.query(Contact).filter_by(phone_number=self.selected_contact).first()
            session.delete(self.contact)
            session.commit()
            self.contact = None
            self.selected_contact = None
            self.populate_model()

    def on_call_button(self, button):
        if self.selected_contact is not None:
            self.contact = session.query(Contact).filter_by(phone_number=self.selected_contact).first()
            self.contact.last_called = datetime.now()
            session.commit()
            self.selected_contact = None
            self.contact = None
            self.populate_model()

    def on_see_button(self, button):
        if self.selected_contact is not None:
            self.contact = session.query(Contact).filter_by(phone_number=self.selected_contact).first()
            self.contact.last_seen = datetime.now()
            session.commit()
            dialog = ContactDialog(self, self.contact, True)
            dialog.run()
            dialog.destroy()
            self.selected_contact = None
            self.contact = None
            self.populate_model()

    def populate_model(self):
        self.contacts_liststore.clear()
        for row in session.query(Contact).order_by(Contact.surname).all():
            elem = [row.name, row.surname, row.email, row.phone_number,
                    "" if row.last_called is None else str(row.last_called),
                    "" if row.last_seen is None else str(row.last_seen)]
            self.contacts_liststore.append(elem)


if __name__ == "__main__":
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()

    win = Window()
    win.connect("delete-event", Gtk.main_quit)
    Gtk.main()
