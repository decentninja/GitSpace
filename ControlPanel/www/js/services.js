angular.module('gitSpace.services', ['ngSocket'])
.factory('Repositories', ['$http', '$rootScope', 'ngSocket', 'settings', function ($http, $rootScope, ngSocket, settings) {

    var repositories = [];
    var ws = null;

    var url = "ws://127.0.0.1:8080";
    var ls = false; // LocalStorage
    if(typeof(Storage) !== "undefined") {
        ls = true;
        var tempUrl = localStorage.getItem("gitSpaceWsUrl");
        if(tempUrl !== null) {
            url = tempUrl;
        }
    }

    function init(url) {
        console.log("Init for url", url);
        $rootScope.rootScope.error = null;
        if(ws !== null) {
            ws.close();
        }
        ws = ngSocket(url);
        setTimeout(function () {
            console.log("Timeout ended, socket readystate =", ws.socket.readyState);
            if(ws.socket.readyState == 3 || ws.socket.readyState === 0) {
                // Socket is closed...
                console.log("Sending websocketsError...");
                $rootScope.$broadcast("websocketsError");
            }
        }, 3000);
        ws.onOpen(function() {
            console.log("Open!");
        });
        ws.onMessage(function (data) {
            // Emitting connected client
            console.log("On message", data);
            var json;
            try {
                json = JSON.parse(data.data);
            } catch (e) {
                $rootScope.rootScope.error = "Invalid JSON from server.";
            }
            console.log("JSON from server:", json);
            repositories = json.data;
            console.log("Repositories from server", repositories);
            $rootScope.$broadcast("dataAvailable");
            //ws.$emit('clientConnected', 'A client connected!');
            //ws.$emit('initialState', JSON.stringify({data:[{name:"Web Client",users:[{name:"Dean Martin",mail:"dean@martin.com",image:"data:image/jpeg;base64,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"},{name:"Frank Sinatra",mail:"frank@sinatra.com",image:"data:image/jpeg;base64,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"},{name:"Robbie Williams",mail:"robbie@williams.com",image:"data:image/jpeg;base64,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"}]},{name:"Android Application",users:[{name:"Dean Martin",mail:"dean@martin.com",image:"data:image/jpeg;base64,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"}]},{name:"Server",users:[{name:"Robbie Williams",mail:"robbie@williams.com",image:"data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAkGBwgHBgkIBwgKCgkLDRYPDQwMDRsUFRAWIB0iIiAdHx8kKDQsJCYxJx8fLT0tMTU3Ojo6Iys/RD84QzQ5OjcBCgoKDQwNGg8PGjclHyU3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3N//AABEIAEgASAMBIgACEQEDEQH/xAAcAAACAwEBAQEAAAAAAAAAAAAGBwAEBQMCAQj/xAA2EAABAwMCAwYFAwMFAQAAAAABAgMEAAURBiESMUETIlFhgZEHFDJxoSPB8BWx0SZjouHxJP/EABgBAAMBAQAAAAAAAAAAAAAAAAIDBAEA/8QAJBEAAgICAQQBBQAAAAAAAAAAAQIAEQMhEiIxMkFRBGFx0fD/2gAMAwEAAhEDEQA/AFbppxLcpglXCCcLwnfB2/tRjY+O03ZhxCXQpl3PCoHCx4c8eQ9KBrSAnCjjONhuM+ufvR6opeahzUA8S0cKuEnZadiDjyI9qrT194Y2hHx/fqGnxdsjl509GuMFAcVHUFqGNyg/+0jFR0BQ7Z9LSVpylSuZHLkPtX6D0VeUts/0udhUYJwhat8DqFeW9AbEBu2/Ee5BMBLrPaOojIPe/T2xwA7E56edT9WIlTCB51AG022PLmobS+HMHkNifPntW5qu1tJz2TaUhAHdGBTWXCt9wt7HBYHIc4OhLOYiUrORknKM4GB16iuErQ0q7Oj5stxWSRxkd5ahvkAdPenI68dxbCjFl8M9LOX3VEZxbf8A8UJYfkLI2ODlKPuSPYGnJfpHzE/gASptk8J4hzPXp9h6VaZYt+mbb8ham0oXzwN1FWPqV5/zlWUpA4HMI2XknzPWsUW1+plzkTtxIxzyN9sfb8VK+rUAspWMJwVcjttn3qUyDEbbYinZ6YUdKnXi4Wg1556U2dP6UYt7aGbteURlnvCOCnuk8s/wUMfB8sTdaOSH20h1MdTjaOpOADj3PvVhUpT8uTKn5bkLfPFkY4VE/Tjx3wB5CkpybV1UofipNC77fiGMvTa7Qy2/26ZMVRAQ4nAAB6HHvn0oU1RPXatTQpTCAYzbKVuNo3KCskZ8MfpJ2+9XtVaouWm7KxamUMOf1RfahxZ7TsW+7nAxjc7j7GuWkoiZraLhOlLlOTIranFLJKkOA5AT4DvK2G3vWOxZaMzGp56h5pa6M391Vxtktl3DfZEFa8JI6FOcZ88ZqzcJdwbcW0+otj/bHMeRoG19qZyzPwWLEtLDrSFOP8KAUq4/pQRy6KPsaLI09+86atUt9OJLkVtxxaRsSpAO3rWKtUTBc2SB6nmJEemrV2Xdwrmse+9dpVrksNcXElzB6eNbDKQ1GaSjAynJI619TkKSR1IB8xWlz6i9XBJ/jRGdWrICUqPEonYY8aldr+kMpnLbGzbTh5+R6V8pwaxc2qNRRQNYuoNkchQ40SRa09n2rSSC/nY8fj19STRLqK8QtQXi0KgQEMvB0uzd9lrBHBj2V0/tQybdpy2Jt7Fxts6S/IhMyVuNyggZWM4Ax0/aiTSNugsxZd1bYUy0guGMha+IhIyBv1NSWANCVDk7dRgfri6rmaiWCOERWksBI5DGScepNEem9exrNYo0F6C4++nPA4gp4VJJJAPUEZI5dKX90dLtykPHi4nFlZCk8JBPMY+9e0OJ4UpAwBkjxBOPxt+TTF2KkxchiRNy8znJ0oy5BHbS1KeITySM8IHoE4+2KcuhbhHn6OtTKCFSGY4aUjOCAgqQNuueCkK20vtlcRxhIAot0Nf0Wa9J7eRhlSkNlkp55z389MEJGOvFnpux/G4OPbV8x3tSkMoLElCkJQcIVz26VHbjFZQVtKLzg+kYwB60JatlW1qM1Mul3uVtYLnAlcPBKj0SRwnbY4OKHYtw05KdDULWupXHTySmMVk+zdLFGEwrvCvU0ltOlrm6VLMn5Z1RX0+k/vUrKOkzdmVRmtX3cNPoKFtyI6e8FePLpUrefHVQibi81d3dTMMpB/QgRm8EdQ2Dt70x4KmU2HT7qkN8CQ2QkDAIABx77+lLfVx/1xdNwQ0ptGeWCG0j9qKLVL+c0hbSrIEZ3syArB5H9waDjyKgxgauREA9dxUxtWXZttScIkHAJxsQDt71iJWQFDAwpODt/MVc1BMdnXuc+4skreUOfMDYfgVVZQ6QvgST3dxWrcQ9XqajSu8VLWd1HJ548c4361nvlSn+IZ4uQOBXdToK3Wkd5BWQD4jkD/1XiaCZaD3ipwgk5ySf80xjawF8oxNQEu/CdHzZUt9C2loUo7kqV/jNUvhqhlFsddWklfbk7DOwA51Z+IrwtmjLZaCkIfdWnjQDnCW043P3Ka8/DdLZshSs4JcUR3fPx8NqHBox2U2YyLIkG4R1Ja4d+mNhipXGxvsNTkFUkJVhQS2tYHIHkNt6ldm8oCi4lpN0Mq6vybhbWzLfVxuKClbk+Q2rZsMyPIluQxCtcZb4S2lUrILhwQkA4JTkjHEOpGedSpXKScYaP+owrjzMg7A1MZNwsgeDQ08wpzkoLkOjCuo5/mty0f0aXYLnd29PMINv4OJoPOZWFKCdjxeJFSpR49yRhUpM3TTziu/phtJ6ky3U4/NbuloVn1JcCi22GKiTE/USXrg+Egg7bhJHPoeeKlSuc0JyKC00NdsMOvOv32y/MOw2yP0JT5QE/V9QaCevOgmPqSzRWHG4tlmtMq2UlFzWBv6fevlShbp7Q6uV40zTsl0NM6YfUo+FxVt/xqVKlT5MpU0AJVh+mV1skz//2Q=="}]}]}));
        });
    }

    console.log(url);
    init(url);

    return {
        getIP: function() {
            // TODO: substring av url
            var ip = (url.split(":")[1]).substr(2);
            console.log("Substring för IP", ip);
            return ip;
        },
        getPort: function() {
            var port = parseInt((url.split(":")[2]));
            console.log("Substring för port", port);
            return port;
        },
        emit: function(data) {
            console.log("Emitting:", data);
            return ws.send(data);
        },
        all: function() {
            return repositories;
        },
        byName: function(name) {
            for (var i in repositories) {
                if(repositories[i].name == name) {
                    return repositories[i];
                }
            }
            return null;
        },
        setUrl: function(newUrl) {
            url = newUrl;
            if(ls) {
                localStorage.setItem("gitSpaceWsUrl", url);
            }
            try {
                init(url);
            } catch (e) {
                console.log("Invalid IP:", e);
            }
        },
        reloadWs: function() {
            init(url);
        }
    };
}]);
