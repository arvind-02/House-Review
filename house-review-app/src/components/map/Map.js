import { useEffect, useState } from 'react';
import './Map.css';

const Map = () => {
    const [datasource, setDatasource] = useState(null);
    const [map, setMap] = useState(null);
    const [searchAddress, setSearchAddress] = useState({
        addressLine1: null,
        addressLine2: null,
        city: null,
        state: null,
        zipcode: null,
        country: null
    });
    const [airBNB, setAirBNB] = useState({});
    const [popupOpen, setPopupOpen] = useState(false);
    const [selectedJSON, setSelectedJSON] = useState(null);
    const [selectedAddress, setSelectedAddress] = useState(null);
    const [note, setNote] = useState({});
    const [notes, setNotes] = useState({});
    const [searchHistory, setSearchHistory] = useState([]);
    const [currentBNBs, setCurrentBNBs] = useState([]);
    const [selectedBNB, setSelectedBNB] = useState({});

    useEffect(() => {
        if (localStorage.getItem("notes")) {
            setNotes(JSON.parse(localStorage.getItem("notes")));
        }

        if (localStorage.getItem("searchHistory")) {
            setSearchHistory(JSON.parse(localStorage.getItem("searchHistory")));
        }

        var newMap = new window.atlas.Map("map", {
            authOptions: {
                authType: 'subscriptionKey',
                subscriptionKey: 'IVTFQALdnqPZbzBdQxTS1Lw1xJ_iBomLZXIvxkEtSNs'
            }
        });

        newMap.events.add('ready', function () {
            var newDatasource = new window.atlas.source.DataSource();
            setDatasource(newDatasource);
            newMap.sources.add(newDatasource);
            var resultLayer = new window.atlas.layer.SymbolLayer(newDatasource, null, {
                iconOptions: {
                    image: 'pin-round-darkblue',
                    anchor: 'center',
                    allowOverlap: true
                },
                textOptions: {
                    anchor: "top"
                }
            });
            newMap.layers.add(resultLayer);
            let popup = new window.atlas.Popup();
            newMap.events.add('click', resultLayer, (e) => {
                console.log(e.shapes[0])
                var p = e.shapes[0].getProperties();
                var position = e.shapes[0].getCoordinates();
                if (p.address.airBNB) {
                    var html = `
                        <div class="popup">
                            <h4><a href="${p.address.freeformAddress}">${p.address.freeformAddress}</a></h4>
                            <p>Overall Sentiment: ${p.address.sentiment}</a></p>
                            <p>Occupants: ${p.address.numPeople}</a></p>
                            <p>Price: ${p.address.price}</a></p>
                        </div>`;
                } else {
                    var html = `
                        <div class="popup">
                            <h4>${p.address.freeformAddress}</h4>
                        </div>`;
                }
                popup.setPopupOptions({
                    content: html,
                    position: position
                });
                popup.open(newMap);
                if (p.address.airBNB) {
                    let bnbData = {};
                    bnbData["freeformAddress"] = p.address.freeformAddress;
                    bnbData["numPeople"] = p.address.numPeople;
                    bnbData["price"] = p.address.price;
                    bnbData["reviews"] = p.address.reviews;
                    bnbData["sentiment"] = p.address.sentiment
                    console.log(bnbData);
                    setSelectedBNB(bnbData);
                } else {
                    setPopupOpen(true);
                    setSelectedAddress(p.address.freeformAddress)
                    setSelectedJSON(e.shapes[0].data);
                }
            });
            for (let json of JSON.parse(localStorage.getItem("searchHistory"))) {
                newDatasource.add(json);
            }
        });
        setMap(newMap);
    }, []);

    const handleInput = (e) => {
        let oldSearch = searchAddress;
        oldSearch[e.target.name] = e.target.value;
        setSearchAddress(oldSearch);
    }

    const stringifySearchAddress = () => {
        let address = "";
        for (let key in searchAddress) {
            if (!searchAddress[key]) {
                continue;
            }
            address += (searchAddress[key] + (key === "city" ? "," : "") + " ");
        }
        return address.slice(0, -1);
    }

    const validateSearchAddress = () => {
        for (let key in searchAddress) {
            if (key === "addressLine2" || key === "zipcode" || key === "country") {
                continue;
            }
            if (!searchAddress[key]) {
                return false;
            }
        }
        return true;
    }

    const search = () => {
        if (validateSearchAddress()) {
            const searchQuery = stringifySearchAddress();
            console.log(searchQuery)
            if (datasource && map) {
                let url = `https://atlas.microsoft.com/search/address/json?subscription-key=${window.atlas.getSubscriptionKey()}&api-version=1.0&query=${searchQuery}&limit=1`;
                fetch(url).then(async (res) => {
                    let json = await res.json();
                    if (json && json.results) {
                        console.log(json);
                        let results = json.results[0];
                        var rawGeoJson = {
                            "type": "Feature",
                            "geometry": {
                                "type": "Point",
                                "coordinates": [results.position.lon, results.position.lat]
                            },
                            "properties": {
                                "address": {
                                    "freeformAddress": searchQuery
                                }
                            }
                        };
                        datasource.add(rawGeoJson);

                        map.setCamera({
                            bounds: [results.position.lon - 0.001, results.position.lat - 0.0005,
                            results.position.lon + 0.001, results.position.lat + 0.0005]
                        });
                    }
                })
            }
        }
    }

    const handleAirBNBSearch = async () => {
        try {
            let res = await fetch(`/api/reviewParser?minPeople=${airBNB.minPeople}&maxPeople=${airBNB.maxPeople}&minPrice=${airBNB.minPrice}&maxPrice=${airBNB.maxPrice}&minScore=${airBNB.minScore}&maxScore=${airBNB.maxScore}`);
            let text = await res.text();
            let json = JSON.parse(text);
            if (datasource) {
                let toRemove = [];
                for (let id of datasource.toJson().features) {
                    if (id.properties.address.airBNB) {
                        toRemove.push(id.id);
                    }
                }
                datasource.remove(toRemove)
                setCurrentBNBs(json);
                for (let id in json) {
                    var rawGeoJson = {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [json[id][1][1], json[id][1][0]]
                        },
                        "properties": {
                            "address": {
                                "freeformAddress": json[id][2],
                                "airBNB": true,
                                "reviews": json[id][0],
                                "numPeople": json[id][3],
                                "price": json[id][4],
                                "sentiment": json[id][5]
                            }
                        }
                    };
                    datasource.add(rawGeoJson);
                }
            }
        } catch(err) {
            console.log(err);
        }
    }

    const handleNoteInput = (e) => {
        setNote(e.target.value);
    }

    const saveNote = () => {
        let oldNotes = notes;
        oldNotes[selectedAddress] = note;
        localStorage.setItem("notes", JSON.stringify(oldNotes));
        let oldSearchHistory = searchHistory;
        oldSearchHistory.push(selectedJSON);
        setSearchHistory(oldSearchHistory);
        localStorage.setItem("searchHistory", JSON.stringify(oldSearchHistory));
    }

    const handleAirBNBInput = (e) => {
        let oldAirBNB = airBNB;
        oldAirBNB[e.target.name] = e.target.value;
        setAirBNB(oldAirBNB);
    }


    return (
        <div>
            <div id="map"></div>
            <div className="dashboard">
                <div className="searchForm">
                    <p>Your notes</p>
                    <input name="addressLine1" className="formInput" placeholder="Address Line 1" onChange={handleInput}></input>
                    <input name="addressLine2" className="formInput" placeholder="Address Line 2" onChange={handleInput}></input>
                    <input name="city" className="formInput" placeholder="City" onChange={handleInput}></input>
                    <input name="state" className="formInput" placeholder="State" onChange={handleInput}></input>
                    <input name="zipcode" className="formInput" placeholder="Zipcode" onChange={handleInput}></input>
                    <input name="country" className="formInput" placeholder="Country" onChange={handleInput}></input>
                    <button className="formInput formButton" onClick={search}>Search</button>
                </div>
                <div><h1>OR</h1></div>
                <div className="searchForm">
                    <p>Apartment Search</p>
                    <input name="minPrice" className="formInput" placeholder="Minimum Price" onChange={handleAirBNBInput}></input>
                    <input name="maxPrice" className="formInput" placeholder="Maximum Price" onChange={handleAirBNBInput}></input>
                    <input name="minPeople" className="formInput" placeholder="Minimum Occupants" onChange={handleAirBNBInput}></input>
                    <input name="maxPeople" className="formInput" placeholder="Maximum Occupants" onChange={handleAirBNBInput}></input>
                    <input name="minScore" className="formInput" placeholder="Minimum Score" onChange={handleAirBNBInput}></input>
                    <input name="maxScore" className="formInput" placeholder="Maximum Score" onChange={handleAirBNBInput}></input>
                    <button className="formInput formButton" onClick={handleAirBNBSearch}>Search</button>
                </div>
            </div>
            {popupOpen &&
                <div className="noteForm">
                    <hr></hr>
                    <h3>{selectedAddress}</h3>
                    <textarea placeholder="Add a note" rows="10" cols="50" onChange={handleNoteInput} value={notes[selectedAddress]}></textarea>
                    <button className="formInput formButton" onClick={saveNote}>Add Note</button>
                </div>
            }
            {selectedBNB.reviews && 
                <div className="airBNB">
                    <hr></hr>
                    <h3><a href={selectedBNB.freeformAddress}>{selectedBNB.freeformAddress}</a></h3>
                    <p>Price: {selectedBNB.price}</p>
                    <p>Number of Occupants: {selectedBNB.numPeople}</p>
                    <p>Sentiment: {selectedBNB.sentiment}</p>
                    <p style={{fontWeight: "bold"}}>Reviews</p>
                    <ul>
                        {selectedBNB.reviews.map((review, idx) => (
                            review === "." ? null : <li key={idx}>{review}</li>
                        ))}
                    </ul>
                </div>
            }
        </div>
    );
}

export default Map;