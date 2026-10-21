#pragma once

#include "Socket.h"

namespace pr {

/*
abstract base class
It defines what a connection handler must be able to do, but not how it does it.
*/

// une interface pour gerer la communication
class ConnectionHandler {
public:
	// gerer une conversation sur une socket
	virtual void handleConnection(Socket &s) = 0; // Modified ajouter &
	// une copie identique
	virtual ConnectionHandler * clone() const = 0;
	// pour virtual
	virtual ~ConnectionHandler() {}

    /*
    * virtu : allows polymorphism (calling the derived class’s version via a base pointer)
    */
};

} // ns pr
