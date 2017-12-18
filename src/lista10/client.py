import gi
import os

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from datetime import datetime
import requests
import json

headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json; charset=UTF-8'
}

uri = 'http://localhost:5000/api/contacts'


class Contact:
    def __init__(self, name, surname, email, phone_number, last_called, last_seen):
        self.id = 0
        self.name = name
        self.surname = surname
        self.email = email
        self.phone_number = phone_number
        self.last_called = last_called
        self.last_seen = last_seen

    def __repr__(self):
        return "<Contact(id='%s', name='%s', surname='%s', email='%s', phone_number='%s' , last_called='%s')>" % (
            self.id, self.name, self.surname, self.email, self.phone_number, self.last_called)

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'surname': self.surname,
            'email': self.email,
            'phone_number': self.phone_number,
            'last_called': None if self.last_called is None else self.last_called,
            'last_seen': None if self.last_seen is None else self.last_seen
        }


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
        name = self.name_entry.get_text()
        surname = self.surname_entry.get_text()
        email = self.email_entry.get_text()
        phone_number = self.phone_entry.get_text()
        c = Contact(name, surname, email, phone_number, None, None)
        return c

    def update_contact(self):
        self.contact.name = self.name_entry.get_text()
        self.contact.surname = self.surname_entry.get_text()
        self.contact.email = self.email_entry.get_text()
        self.contact.phone_number = self.phone_entry.get_text()

        return self.contact


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
        self.contacts_liststore = Gtk.ListStore(int, str, str, str, str, str, str)
        self.populate_model()

        # Init filter
        self.current_filter_contacts = None
        self.contacts_filter = self.contacts_liststore.filter_new()
        self.contacts_filter.set_visible_func(self.contacts_filter_func)

        # Init tree view
        self.contacts_treeview = Gtk.TreeView.new_with_model(self.contacts_filter)
        for i, column_title in enumerate(
                ["ID", "Name", "Surname", "Email", "Phone Number", "Last Called", "Last Seen"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            self.contacts_treeview.append_column(column)

        self.selected_contact = None
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
            self.selected_contact = model[treeiter][0]

    def on_add_button(self, button):
        dialog = ContactDialog(self, None, False)
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            contact = dialog.create_contact()
            requests.post(uri, json=contact.serialize())
        self.clear_selection()
        dialog.destroy()

    def on_update_button(self, button):
        if self.selected_contact is not None:
            dialog = ContactDialog(self, self.get_contact(self.selected_contact), False)
            response = dialog.run()

            if response == Gtk.ResponseType.OK:
                updated = dialog.update_contact()
                requests.put(os.path.join(uri, str(self.selected_contact)), json=updated.serialize())
            self.clear_selection()
            dialog.destroy()

    def on_delete_button(self, button):
        if self.selected_contact is not None:
            requests.delete(os.path.join(uri, str(self.selected_contact)))
            self.clear_selection()

    def on_call_button(self, button):
        if self.selected_contact is not None:
            requests.post(os.path.join(uri, str(self.selected_contact), 'call'))
            self.clear_selection()

    def on_see_button(self, button):
        if self.selected_contact is not None:
            dialog = ContactDialog(self, self.get_contact(self.selected_contact), True)
            dialog.run()
            dialog.destroy()
            requests.post(os.path.join(uri, str(self.selected_contact), 'see'))
            self.clear_selection()

    def populate_model(self):
        self.contacts_liststore.clear()
        response = requests.get(uri)
        for item in response.json():
            elem = [item['id'], item['name'], item['surname'], item['email'], item['phone_number'], item['last_called'],
                    item['last_seen']]
            self.contacts_liststore.append(elem)

    def get_contact(self, contact_id):
        item = requests.get(os.path.join(uri, str(self.selected_contact))).json()
        return Contact(item['name'], item['surname'], item['email'], item['phone_number'],
                       item['last_called'],
                       item['last_seen'])

    def clear_selection(self):
        self.selected_contact = None
        self.populate_model()


if __name__ == "__main__":
    win = Window()
    win.connect("delete-event", Gtk.main_quit)
    Gtk.main()
