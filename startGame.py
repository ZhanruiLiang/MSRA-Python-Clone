#! /usr/bin/env python
import shippo

if __name__ == '__main__':
    game = shippo.Shippo()
    game.show_menu()
    if game.wait_connect():
        game.setup_level()
        try:
            game.mainloop()
        except KeyboardInterrupt:
            pass
