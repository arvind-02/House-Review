import { useEffect, useState } from 'react';
import './Map.css';

const Map = () => {
    const [datasource, setDatasource] = useState(null);
    const [map, setMap] = useState(null);
    const [searchAddress, setSearchAddress] = useState({
        addressLine1: "2949 Bell Blvd",
        addressLine2: null,
        city: "Bayside",
        state: "NY",
        zipcode: "11360",
        country: "USA"
    });
    const [zillowURL, setZillowURL] = useState(null);
    const [popupOpen, setPopupOpen] = useState(false);
    const [selectedJSON, setSelectedJSON] = useState(null);
    const [selectedAddress, setSelectedAddress] = useState(null);
    const [note, setNote] = useState({});
    const [notes, setNotes] = useState({});
    const [searchHistory, setSearchHistory] = useState([]);

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
                var html = `
                    <div class="popup">
                        <h4>${p.address.freeformAddress}</h4>
                    </div>`;
                popup.setPopupOptions({
                    content: html,
                    position: position
                });
                popup.open(newMap);
                setPopupOpen(true);
                setSelectedAddress(p.address.freeformAddress)
                setSelectedJSON(e.shapes[0].data);
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

    const handleZillowInput = (e) => {
        setZillowURL(e.target.value);
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

    const handleZillowSearch = async () => {
        try {
            let res = await fetch("/api/reviewParser");
            let text = await res.text();
            console.log(text);
            // let json = await res.json();
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

    return (
        <div>
            <div id="map"></div>
            <div className="dashboard">
                <div className="searchForm">
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
                    <input name="addressLine1" className="formInput" placeholder="Zillow URL" onChange={handleZillowInput}></input>
                    <button className="formInput formButton" onClick={handleZillowSearch}>Search</button>
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
        </div>
    );
}

export default Map;