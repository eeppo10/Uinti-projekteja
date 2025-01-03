"""
- COMP.CS.100 -
Tekijä: Eerikki Laitala
S-posti: eerikki.laitala@gmail.com
Projekti: Graafinen käyttöliittymä
                -Ohjelman kuvaus-

Tämän ohjelman tarkoituksena on toimia Suomen uimaliiton uintivalmentajille
saatavilla olevien tilastotiedostojen nopeana ja helppona selaimena.
Tiedostosta on mahdollista:
- Hakea lajin, sarjan ja tekstin perusteella
- Valita tulostettavat tiedot esim. paikka, päivämäärä, pisteet...



                -Tilastotiedosto-

Ohjelma ottaa vastaan .CSV tyyppisen tiedoston, jonka rakenne on seuraava:
-----------------------------
otsikko1,otsikko2,Laji,Luokka,...
data1,data2,Laji1,Mies,...
....,...,Laji2,Nainen,...
-----------------------------
Tiedoston muodon täytyy siten olla otsikkot jotka sisältävät lajin
 ja luokan (Mies tai Nainen).
Jos otsikko puuttuu tiedostolle suoritetut suodatukset eivät toimi.

Uimaliitolta saatavassa tiedostossa asema, eli sijoitus tilastoissa esitetään
FINA-piste järjestyksessä, jolloin naisia ja miehiä voidaan vertailla yhdessä
taulukossa. Tulostettaessa vain toinen sarjoista muokataan asemaa vastaamaan
sijoitusta kyseissessä sarjassa. Hakua käytettäessä pysyy sijoitus samana
kuin se oisi kokonaistilastoissa.

FINA-pisteiden ohella tiedostossa on myös SUil pisteet jotka kertovat
tuloksen tason omaan ikäryhmään nähden Suomen tilastoissa.

                -Käyttöohje-

Tiedoston Valinta:
- Ohjelma avaa ensin tiedoston valintaikkunan
- Oikeantyyppisen tiediston valittua aukeaa pääikkuna
- Väärän tiedoston avaamisesta kerrotaan virheviestillä

Pudotusvalikot:
- Pääikkunassa on kaksi pudotusvalikkoa, joista valitaan suodatusperuste lajin
 tai teksin mukaan, sekä kilpailuluokka eli miesten-, naisten-sarja tai kaikki
- Tiedot päivittyvät haku-nappia painamalla
- Jos hakutermiä/lajia ei ole syötetty ilmoittaa ohjelma siitä tekstikentässä

Tekstihaku:
- Tekstihaku toimii siten että se vastaanottaa vähintään yhden termin,
    jonka perusteella tulosteet suodatetaan
- Hakutermejä voi olla useita, jolloin ne erotellaan pilkulla (Termi1,Termi2,..)
- Hakutermin ei tarvitse olla täysin sama kuin haettavan termin,
    mutta esim. välilyöntien tulee olla paikallaan.
- Hakua ei ole mahdollista suorittaa lajin ollessa valittuna, tällöin hakukenttä
    tyhjenee haku-nappulaa painettaessa

Valintalaatikot:
- Tulostekentän yläpuolella olevista valintalaatikoista voi määrittää, mitkä
    tiedot haluaa datasta tulostettavan
- Laatikoiden määrä riippuu tiedostossa olevien otsikoiden määrästä ja
  ne luodaan automaattisesti tiedoston lukemisen jälkeen otsikoiden perusteella

Ohjelman sulkeminen:
- Ikkunan oikeassa ylänurkassa on sulje painoke, ohjelman suoritus lopppuu tätä
    painamalla


"""
# Libraries
import csv
from tkinter import *
from tkinter.scrolledtext import ScrolledText
from tkinter import filedialog
from tkinter import messagebox

# Genders for series selection
GENDERS = {"Miehet": "Mies", "Naiset": "Nainen", "Kaikki": "Kaikki"}
# Fixed size for every field possible to be shown from a ranking .csv
FIELD_SIZES = {'Asema': 6, 'Uimari': 25, 'Syntynyt': 8, 'Seura': 12,
               'Kilpailu': 40, 'Laji': 16, 'Allas': 5, 'Kierrosyyppi': 7,
               'Pvm': 10, 'Paikka': 15, 'Aika': 9, 'Fina-pisteet': 4,
               'Suil pisteet': 5, 'Luokka': 8}

# Text box size
BOX_WIDTH = 215
BOX_HEIGHT = 70


class Userinterface:

    def __init__(self, data, events, fieldnames):
        """
        Ui components, variables, data handling,and settings
        """

        # Mainwindow
        self.__mainwindow = Tk()
        self.__mainwindow.title("Tilastoselain")

        # Data objects
        self.__data = data
        self.__events = events
        self.__fieldnames = fieldnames

        # Output window for event data
        self.__st = ScrolledText(self.__mainwindow, width=BOX_WIDTH,
                                 height=BOX_HEIGHT)

        # Menu components
        self.__menu = StringVar(value="Ei valittuna")
        self.__mainmenu = OptionMenu(self.__mainwindow, self.__menu,
                                     "Hae tekstin perusteella", *self.__events)
        self.__gender = StringVar(self.__mainwindow, value="Kaikki")
        self.__gender_dd = OptionMenu(self.__mainwindow, self.__gender,
                                      "Miehet", "Naiset", "Kaikki")

        # Check boxes
        self.__cb = {}
        self.__checkbutton = {}
        self.create_boxes()

        # Buttons
        self.__button_exit = Button(self.__mainwindow, text="Sulje",
                                    bg='pink', command=self.stop)
        self.__button_search = Button(self.__mainwindow, text="Hae tiedot",
                                      bg='lightblue',
                                      command=self.get_event_data)

        # Text components
        self.__label_event = Label(self.__mainwindow, text="Valitse laji:")
        self.__label_show = Label(self.__mainwindow, text="Näytä:")
        self.__label_gender = Label(self.__mainwindow, text="Sarja:")
        self.__label_search = Label(self.__mainwindow, text="Etsi:")

        # Text box
        self.__search = StringVar(value="")
        self.__search_box = Entry(self.__mainwindow,
                                  textvariable=self.__search)

        # Interface layout for fixed components
        self.__st.grid(row=3, columnspan=20, rowspan=20)
        self.__label_event.grid(row=0, column=0)
        self.__mainmenu.grid(row=1, column=0)
        self.__label_gender.grid(row=0, column=1)
        self.__gender_dd.grid(row=1, column=1)
        self.__button_search.grid(row=0, column=2)
        self.__button_exit.grid(row=0, column=19)
        self.__label_show.grid(row=1, column=2)
        self.__label_search.grid(row=0, column=3)
        self.__search_box.grid(row=0, column=4)

    def create_boxes(self):
        """
        Creates boxes for ui depending on files fieldnames
        """
        # Initializing button data
        fieldnames = self.__fieldnames
        placement = 3

        # Creating buttons depending on the amount of fieldnames
        for headers in fieldnames:
            self.__cb[headers] = StringVar(self.__mainwindow, value=headers)
            self.__checkbutton[headers] = Checkbutton(self.__mainwindow,
                                                      text=str(headers),
                                                      variable=self.__cb[
                                                          headers],
                                                      onvalue=headers)
            self.__checkbutton[headers].grid(row=1, column=placement,
                                             sticky='W')
            placement += 1

    def stop(self):
        """
        Ends the execution of the program.
        """
        self.__mainwindow.destroy()

    def start(self):
        """
        Starts the mainloop.
        """
        self.__mainwindow.mainloop()

    def get_box_state(self):
        """
        Get the state of tick boxes
        :return state_list:
        """
        # Get and initialize data
        fieldnames = self.__fieldnames
        state_list = []

        # Get data
        for header in fieldnames:
            state_list.append(self.__cb[header].get())

        return state_list

    def print(self, row):
        """
        Printing out the data into text box
        :param row:
        :return None:
        """
        # Getting box states and headers
        box_state = self.get_box_state()
        header = self.__fieldnames
        data_print = ""

        # Forming string according to needs
        for field_names in box_state:
            if field_names in header:
                data_print += f"| {row[field_names][:FIELD_SIZES[field_names]]:<{FIELD_SIZES[field_names]}}"

        # Insert line to text field
        self.__st.insert('insert', data_print + "\n")

    def print_header(self):
        """
        Prints header for event data
        :param self:
        :return None:
        """

        # Data
        box_state = self.get_box_state()
        header = self.__fieldnames

        # Initialize text variable
        header_print = ""

        # Insert header to text field
        for field_names in box_state:
            if field_names in header:
                header_print += f"| {field_names[:FIELD_SIZES[field_names]]:<{FIELD_SIZES[field_names]}}"
        self.__st.insert('insert', header_print + "\n")

        # Insert bottom of header to text field
        for i in range(0, BOX_WIDTH - 2):
            self.__st.insert('insert', "-")
        self.__st.insert('insert', "-" + "\n")

    def print_event(self):
        """
        Print event data in text box
        :param self:
        :return None:
        """
        # Data
        event = self.__menu.get()
        box_state = self.get_box_state()
        header = self.__fieldnames
        counter = 0

        # Gender / class data
        gender = self.__gender.get()
        gender = GENDERS[gender]

        # Go through data
        for row in self.__data:
            # Initialize print line
            data_print = ""

            # Form printed line for gender specific results
            if row["Laji"] == event and row["Luokka"] == gender:
                # Counter for rank since data is in FINA points order for all
                counter += 1

                # Insert rank
                for field_names in box_state:
                    if field_names == "Asema":
                        data_print += f"| {str(counter)[:FIELD_SIZES[field_names]]:<{FIELD_SIZES[field_names]}}"

                    elif field_names in header:
                        data_print += f"| {row[field_names][:FIELD_SIZES[field_names]]:<{FIELD_SIZES[field_names]}}"

                # Insert line to text field
                self.__st.insert('insert', data_print + "\n")

            # Form printed line for ranking including all swimmers
            elif row["Laji"] == event and gender == "Kaikki":
                self.print(row)

    def text_search(self):
        """
        Searches for data in the fields
        :return None:
        """
        # Get search terms
        terms = self.__search.get().casefold()
        terms = terms.split(',')

        # Gender / Class data
        gender = self.__gender.get()
        gender = GENDERS[gender]

        # If there is no search terms
        if len(terms[0]) < 1:
            self.__st.delete(1.0, END)
            self.__st.insert('insert',
                             "Ei hakutermejä, syötä vähintään yksi hakutermi" + "\n")
            return

        if gender == "Kaikki":
            for row in self.__data:
                # Initialize hit counter
                counter = 0

                # Test for term hits
                for field in row:
                    if any((row[field].casefold()).startswith(x) for x in
                           terms):
                        counter += 1
                # If enough hits print
                if len(terms) == counter:
                    self.print(row)

        else:
            for row in self.__data:
                # Initialize hit counter
                counter = 0

                # Check for term hits
                for field in row:
                    if any(row[field].casefold().startswith(x) for x in terms) \
                            and row["Luokka"] == gender:
                        counter += 1
                # If enough hits print
                if len(terms) == counter:
                    self.print(row)

    def get_event_data(self):
        """
        Print event result information on the text block
        As user has requested
        :return None:
        """

        # Data elements
        event = self.__menu.get()

        # Make text window writable
        self.__st.configure(state='normal')

        # Initialize text field
        self.__st.delete(1.0, END)

        # If no event is selected give feedback
        if event not in self.__events:
            if event != "Hae tekstin perusteella":
                self.__st.insert('insert',
                    "Ei toimintoa valittuna valitse haku parametrit!" + "\n")
                return

        # Prints header
        self.print_header()

        # Print data
        if event == "Hae tekstin perusteella":
            self.text_search()
        else:
            # Clear search box
            self.__search_box.delete(0, END)
            # Print event data
            self.print_event()

        # Make text window read only
        self.__st.configure(state='disabled')


def read_file():
    """
    Reads the included results or rankings file ()
    :return data, fieldnames:
    """
    # Initialize data list
    data_list = []

    # Opening file
    filename = filedialog.askopenfilename()
    with open(filename, encoding='utf8', newline='') as csvfile:

        data = csv.DictReader(csvfile, dialect='excel')

        # Get field headers
        fieldnames = data.fieldnames



        # Save data into a list
        for row in data:
            if fieldnames[1] == row[fieldnames[1]]:
                pass
            if row[fieldnames[1]] == "":
                pass
            else:
                data_list.append(row)

    # Test for required fields
    try:
        test_event = data_list[1]["Laji"]
        test_gender = data_list[1]["Luokka"]

    # If required fields not found
    except:
        # Causes Error message to be shown
        return

    return data_list, fieldnames


def get_events(data):
    """
    Get list of events present in the list
    :param data:
    :return events:
    """
    # Initialize list of events
    events = []

    # Get events
    for row in data:
        if row["Laji"] not in events:
            if row["Laji"] != "Laji":
                events.append(row["Laji"])

    return events


def main():
    """
    Main loop this is where the magick happens
    """
    # Try to get data
    try:
        data, fieldnames = read_file()

    # If file is unsupported
    except:
        messagebox.showerror('File Error',
                             'Encountered an error while reading file')
        return

    # Start ui
    ui = Userinterface(data, get_events(data), fieldnames)
    ui.start()


if __name__ == "__main__":
    main()
