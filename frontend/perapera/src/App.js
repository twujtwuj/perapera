import React, {useState, useEffect} from 'react'  // react hooks used for API endpoints
import api from './api'

// useState hook: keep a state within React, so we know when state changes, when to shift and change pieces of data
// useEffect hook: when component loads (App.js), then fetch transactions

const App = () => {
  const [card, setCard] = useState([]);
  const [showAnswer, setShowAnswer] = useState(false);

  // Get the next card
  const fetchNextCard = async () => {
    const response = await api.get('/next_card')  // next card port
    setCard(response.data)
    setShowAnswer(false);
  }

  // Initialise the first card on component mount
  useEffect(() => {
    fetchNextCard();
  }, [])

  // Show answer button click
  const showAnswerButtonClick = () => {
    setShowAnswer(true);
  }

  // Review button click
  const reviewButtonClick = async (rating) => {
    // Make the API call to update card with the selected review level
    await api.put(`/next_card_review?rating=${rating}`);
    fetchNextCard();
  };

  // HTML stuff is from boostrap; can only return one things as a paretn
  return (

    <div>

      {/* Display  */}
      <nav className='navbar navbar-dark bg-primary'>
        <div ClassName='container-fluid'>
          <a className='navbar-brand' href='#' style={{ marginLeft: '20px' }}>
            PeraPera ペラペラ
          </a>
        </div>
      </nav>

      {/* Display kanji */}
      <div className='card-container' style={{ textAlign: 'center', padding: '20px' }}>
        <h1 style={{ fontSize: '136px', fontFamily: 'YuMincho' }}>{card.kanji}</h1>
      </div>

      {/* Show answer button */}
      {!showAnswer && (
        <div className='button-container' style={{ display: 'flex', justifyContent: 'center', marginTop: '20px' }}>
          <button type='button' className='btn btn-primary' style={{ marginRight: '10px' }} onClick={showAnswerButtonClick}>
            Show answer
          </button>
        </div>
      )}

      {/* Display card information and review buttons when showAnswer is true */}
      {showAnswer && (

        <div>

          {/* Display card information in a table */}
          <table className="table table-bordered" style={{ marginTop: '20px' }}>
            <thead>
              <tr>
                <th scope="col">Kun Reading</th>
                <th scope="col">On Reading</th>
                <th scope="col">Next review date</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>{card.readings_kun}</td>
                <td>{card.readings_on}</td>
                <td>{card.next_review}</td>
              </tr>
            </tbody>
          </table>

          {/* Review buttons */}
          <div className='button-container' style={{ display: 'flex', justifyContent: 'center', marginTop: '20px' }}>
            <button type='button' className='btn btn-danger' style={{ marginRight: '10px' }} onClick={() => reviewButtonClick(1)}>
              Unknown
            </button>
            <button type='button' className='btn btn-warning' style={{ marginRight: '10px' }} onClick={() => reviewButtonClick(2)}>
              Hard
            </button>
            <button type='button' className='btn btn-success' style={{ marginRight: '10px' }} onClick={() => reviewButtonClick(3)}>
              Okay
            </button>
            <button type='button' className='btn btn-primary' onClick={() => reviewButtonClick(4)}>
              Easy
            </button>

          </div>

        </div>

      )}
    </div>
  );
}

export default App;

