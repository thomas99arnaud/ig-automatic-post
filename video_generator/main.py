from . import _0_general , _80_netlify_depolyment

SUJET = "dog"
NOMBRE_DE_VIDEOS = 10
#langues = ["francais", "anglais", "espagnol", "portugais"]
langues = ["francais"]

SUJETS = ["koala","penguin","giraffe","parrot","whale","sheep","swan","arctic fox","border collie","hamster","dolphin", "wolf","cockatoo","kangaroo","pitbull","british shorthair","rabbit","horse",
    "capuchin monkey","iguana","maine coon","lion","hedgehog","chimpanzee","scottish fold","boxer dog","cow","goat","chameleon","seal","panda","penguin","gecko","pug",
    "persian cat","corgi","donkey","red panda","deer","leopard","dalmatian","hummingbird","huskies","golden retriever","rottweiler","goose","chipmunk","squirrel","zebra","siamese cat","tortoise",
    "sea lion","flamingo","elephant","rhinoceros","labrador","monkey","rabbit","fox","owl","jaguar","donkey","tiger","french bulldog","beagle","pony","turtle","alaskan malamute","ferret",
    "moose","sphynx cat","peacock","bear","red panda","hippopotamus","tortoise","cat","dog","frog","bengal cat","greyhound","dalmatian","seal","hamster","goose",
    "wallaby","otter","chihuahua","eagle","reindeer"]

_0_general.lanceur(SUJET, langues, NOMBRE_DE_VIDEOS)
#_80_netlify_depolyment.deploy_videos()