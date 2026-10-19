"""Stopwords for the "words you could not stop saying" card. Standard library only.

Function words for English, German, Italian and Spanish (plus short Portuguese and French lists), common chat
filler in those languages, and the placeholders WhatsApp writes for media. Words are lowercase; apostrophes are
kept so both "don't" and "dont" are listed.
"""

EN = """
a about above across after afterwards again against ago ah all almost alone along already also although always am among an
and another any anybody anyhow anyone anything anyway anyways anywhere are aren't around as at away be became because become
becomes been before beforehand behind being below beside besides between beyond both but by can can't cannot could couldn't
did didn't do does doesn't doing don't done down during each either else elsewhere enough etc even ever every everybody
everyone everything everywhere except few for former formerly from further had hadn't has hasn't have haven't having he he'd
he'll he's hence her here here's hereby herein hers herself him himself his how how's however i i'd i'll i'm i've ie if in
indeed instead into is isn't it it'd it'll it's its itself just least less let let's like likely ma many may maybe me
meanwhile might mine more moreover most mostly much must mustn't my myself namely neither never nevertheless next no nobody
none noone nor not nothing now nowhere of off often on once one only onto or other others otherwise ought our ours ourselves
out over own per perhaps please quite rather re really same seem seemed seeming seems several shall shan't she she'd she'll
she's should shouldn't since so some somebody somehow someone something sometime sometimes somewhat somewhere still such than
that that'll that's thats the their theirs them themselves then thence there there's thereafter thereby therefore therein
these they they'd they'll they're they've this those though through throughout thru thus to together too toward towards under
unless until up upon us very via was wasn't we we'd we'll we're we've were weren't what what's whatever when when's whence
whenever where where's whereas wherever whether which while whither who who's whoever whole whom whose why why's will with
within without won't would wouldn't yet you you'd you'll you're you've your yours yourself yourselves
im ive id ill youre youve youll theyre theyve dont doesnt didnt cant couldnt wont wouldnt shouldnt isnt arent wasnt werent
hasnt havent hadnt whats hows wheres theres heres lets thats u ur r ya yall y'all gonna wanna gotta kinda sorta dunno lemme
"""

EN_CHAT = """
yes yeah yea yep yup nope nah ok okay okey kk alright aight sure fine cool nice great good bad best better well right wrong
oh ohh ahh hmm hm mm mmm uh um uhm wow omg hey hi hello bye thanks thank thx ty pls plz welcome sorry np yo
one two three four five six seven eight nine ten first second third last next new old big small little long short
day days today tomorrow yesterday tonight morning afternoon evening night week weeks weekend month months year years
time times hour hours minute minutes min mins sec moment now later soon early late
monday tuesday wednesday thursday friday saturday sunday
thing things stuff something anything everything nothing way ways lot lots bit kind sort part number numbers place point
people person guy guys man someone everyone
get got gets getting go goes going gone went come comes coming came make makes made making take takes took taken
know knew known think thought see saw seen look looks looking want wanted need needs needed tell told say says said ask asked
give gave given put keep let try tried call called send sent work works working feel felt mean means meant use used
still also back even much many really actually probably definitely literally basically totally just yet already maybe
message messages chat group text texts link
"""

DE = """
aber alle allem allen aller alles als also am an ander andere anderem anderen anderer anderes anderm andern anders auch auf
aus bei beim bin bis bist da dabei dadurch dafür dagegen daher dahin damals damit danach daneben dann daran darauf daraus darf
darfst darin darum darunter darüber das dass dasselbe davon davor dazu dein deine deinem deinen deiner deines dem demselben den
denn denselben der derer derselbe derselben des desselben dessen deswegen dich die dies diese dieselbe dieselben diesem diesen
dieser dieses dir doch dort du durch dürfen ein eine einem einen einer eines einig einige einigem einigen einiger einiges
einmal er es etwas euch euer eure eurem euren eurer eures für gegen gewesen hab habe haben habt hast hat hatte hatten hätte
hätten hier hin hinter ich ihm ihn ihnen ihr ihre ihrem ihren ihrer ihres im in indem ins ist ja jede jedem jeden jeder jedes
jene jenem jenen jener jenes jetzt kann kannst kein keine keinem keinen keiner keines können könnte machen man manche manchem
manchen mancher manches mein meine meinem meinen meiner meines mich mir mit muss musst müssen musste nach nachdem nein nicht
nichts noch nun nur ob oder ohne sehr sein seine seinem seinen seiner seines selbst sich sie sind so solche solchem solchen
solcher solches soll sollen sollte sondern sonst über um und uns unser unsere unserem unseren unserer unseres unter viel vom
von vor wann war waren warst warum was weg weil weiter welche welchem welchen welcher welches wenn wer werde werden werdet
weshalb wie wieder will wir wird wirst wo woher wohin wollen wollte würde würden zu zum zur zwar zwischen
"""

DE_CHAT = """
ok okay jo joa jaa ne nee nö naja na halt eben mal schon eigentlich einfach gerade grad genau gut super cool klar sicher echt
danke bitte gerne gern hallo hey servus moin tschüss ciao lol haha
heute morgen gestern abend nacht tag tage woche wochen wochenende monat jahr zeit uhr stunde stunden minuten
montag dienstag mittwoch donnerstag freitag samstag sonntag
erste letzte letzten nächste nächsten neue neuen alte großen kleine
ding dinge sache sachen leute mensch nummer
machen mache macht gemacht gehen geht gehe ging kommen komme kommt kam sehen sieh sehe sagen sage sagt gesagt
wissen weiß weißt denke denkst glaube finde brauche brauchst gibt geben
nachricht gruppe
"""

IT = """
a ad agli ai al alla alle allo anche ancora avere aveva avevano avevo abbiamo avete avuto c che chi ci cioè coi col come con
contro cosa cose così cui da dagli dai dal dall dalla dalle dallo degli dei del dell della delle dello dentro di dove e è ed
era erano essere fa fare fino fra gli ha hai hanno ho il in io la le lei li lo loro lui ma me mi mia mie miei mio molto ne
negli nei nel nell nella nelle nello noi non nostra nostre nostri nostro o od ogni per perché però più poi può qual quale
quali qualche quando quanto quella quelle quelli quello questa queste questi questo qui se sei senza si sia siamo siete sono
sta stai stanno stato stesso su sua sue sugli sui sul sull sulla sulle sullo suo suoi ti tra tu tua tue tuo tuoi tutti tutto
un una uno vi voi già sempre mai solo proprio ecco
"""

IT_CHAT = """
sì si ok okay va bene vabbè boh beh dai allora comunque quindi tipo cioè grazie prego ciao ehi ciaooo
oggi domani ieri stasera sera mattina notte giorno giorni settimana weekend mese anno ora ore minuti tempo
lunedì martedì mercoledì giovedì venerdì sabato domenica
primo prima ultimo ultima prossimo prossima nuovo nuova
cosa cose gente persone numero
fare faccio fai fatto vado vai andare vieni venire vedere visto dire detto dico sapere so sai penso credo devo
messaggio gruppo
"""

ES = """
a al algo algunas algunos ante antes como con contra cual cuando de del desde donde durante e el él ella ellas ellos en entre
era eran es esa esas ese eso esos esta está estaba estado estamos están estar estas este esto estos estoy fue fueron ha
habéis había han has hasta hay he la las le les lo los más me mi mis mucho muchos muy nada ni no nos nosotros o os otra otras
otro otros para pero poco por porque que qué quien se sea ser si sí sin sobre son su sus también tanto te tenemos tener tengo
ti tiene tienen todo todos tu tú tus un una uno unos usted vosotros y ya yo
"""

ES_CHAT = """
vale ok okay bueno pues entonces claro gracias hola adiós vamos igual tipo jaja
hoy mañana ayer noche tarde día días semana fin mes año hora horas minutos tiempo
lunes martes miércoles jueves viernes sábado domingo
primero primera último última próximo próxima nuevo nueva
cosa cosas gente número
hacer hago hace hecho voy vas ir ver visto decir dicho digo saber sé sabes creo pienso puedo puedes quiero
mensaje grupo
"""

PT = """
a o os as um uma de do da dos das e que em com por para não sim é são está estou eu você ele ela mas como mais muito já
"""

FR = """
le la les un une des de du et ou que en dans avec pour pas oui non est sont je tu il elle nous vous mais comme plus très
déjà ça
"""

# Placeholders WhatsApp writes instead of media, in several export languages.
PLACEHOLDERS = """
omitted image audio video sticker gif document media attached deleted message edited null weggelassen bild
omessa omesso immagine allegato eliminato omitido imagen adjunto eliminado
"""

STOPWORDS = frozenset(
    w for block in (EN, EN_CHAT, DE, DE_CHAT, IT, IT_CHAT, ES, ES_CHAT, PT, FR, PLACEHOLDERS) for w in block.split()
)
