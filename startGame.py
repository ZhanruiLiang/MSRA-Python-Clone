#! /usr/bin/env python
import shippo

if __name__ == '__main__':
    game = shippo.Shippo()
    game.wait_connect()
    game.setup_level()
    game.mainloop()
