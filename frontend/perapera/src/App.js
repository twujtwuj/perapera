// React
import React, {useState, useEffect} from 'react'  // react hooks used for API endpoints
import api from './api'

// Bootstrap
import 'bootstrap/dist/css/bootstrap.css'
import { Tabs, Tab } from 'react-bootstrap'  // Use tabs
import Table from 'react-bootstrap/Table'  // Use table
import Button from 'react-bootstrap/Button'  // Use table

// useState hook: keep a state within React, so we know when state changes, when to shift and change pieces of data
// useEffect hook: when component loads (App.js), then fetch transactions

const App = () => {

  const [card, setCard] = useState([]);
  const [showAnswer, setShowAnswer] = useState(false);
  const [seenCards, setSeenCards] = useState([]);
  const [formData, setFormData] = useState({
    kanji: '',
    strokes: 0,
    grade: 0,
    freq: 0,
    jlpt_new: 0,
    meanings: '',
    readings_on: '',
    readings_kun: '',
    prev_review: '',
    next_review: '',
    seen: true
  });

  // Get seen cards
  const fetchSeenCards = async () => {
    const response = await api.get('/seen_cards');  // seen cards port
    setSeenCards(response.data);
  };

  // Get the next card
  const fetchNextCard = async () => {
    const response = await api.get('/next_card')  // next card port
    setCard(response.data)
    setShowAnswer(false);
    fetchSeenCards();
  }

  useEffect(() => {
    fetchNextCard();
    fetchSeenCards();
  }, [])

  // Review button click
  const reviewButtonClick = async (rating) => {
    await api.put(`/next_card_review?rating=${rating}`);  // reviewing next card port
    fetchNextCard();
    fetchSeenCards();
  };

  // Show answer when button clicked
  const showAnswerButtonClick = () => {
    setShowAnswer(true);
  }

  // FORM --------------------------
  // Form input
  const handleInputChange = (event) => {
    const value = event.target.value;
    setFormData({
      ...formData,
      [event.target.name]: value,
    });
  };

  const handleFormSubmit = async (event) => {
    event.preventDefault(); // Do not automatically submit the form
    await api.post('/new_card', formData);
    fetchSeenCards();
    setFormData({
      kanji: '',
      strokes: 0,
      grade: 0,
      freq: 0,
      jlpt_new: 0,
      meanings: '',
      readings_on: '',
      readings_kun: '',
      prev_review: '',
      next_review: '',
      seen: true
    })
  }
  // ---------------------------------

  return (

    <div>

      {/* Navigation bar */}
      <nav className='navbar navbar-dark bg-primary'>
        <div ClassName='container-fluid'>
          <a className='navbar-brand' href='#' style={{ marginLeft: '20px' }}>
            PeraPera ペラペラ
          </a>
        </div>
      </nav>
      
      {/* Tabs */}
      <Tabs defaultActiveKey="second">

        <Tab eventKey="first" title="Learn 習う">
          
          {/* Display kanji */}
          <div className='card-container' style={{ textAlign: 'center', padding: '20px' }}>
            <h1 style={{ fontSize: '136px', fontFamily: 'YuMincho' }}>{card.kanji}</h1>
          </div>

          {/* Answer button */}
          {!showAnswer && (
            <div className='button-container' style={{ display: 'flex', justifyContent: 'center', marginTop: '20px' }}>
              <Button type='button' className='btn btn-primary' style={{ marginRight: '10px' }} onClick={showAnswerButtonClick}>
                Show answer
              </Button>
            </div>
          )}

          {/* Card information and review buttons when showAnswer is true */}
          {showAnswer && (

            <div>

              {/* Display card information in a table */}
              <Table className="table table-bordered" style={{ marginTop: '20px' }}>
                <thead>
                  <tr>
                    <th scope="col">Meaning</th>
                    <th scope="col">Kun Reading</th>
                    <th scope="col">On Reading</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>{card.meanings}</td>
                    <td>{card.readings_kun}</td>
                    <td>{card.readings_on}</td>
                  </tr>
                </tbody>
              </Table>

              {/* Review buttons */}
              <div className='button-container' style={{ display: 'flex', justifyContent: 'center', marginTop: '20px' }}>
                <Button type='button' className='btn btn-danger' style={{ marginRight: '10px' }} onClick={() => reviewButtonClick(1)}>
                  Unknown
                </Button>
                <Button type='button' className='btn btn-warning' style={{ marginRight: '10px' }} onClick={() => reviewButtonClick(2)}>
                  Hard
                </Button>
                <Button type='button' className='btn btn-success' style={{ marginRight: '10px' }} onClick={() => reviewButtonClick(3)}>
                  Okay
                </Button>
                <Button type='button' className='btn btn-primary' onClick={() => reviewButtonClick(4)}>
                  Easy
                </Button>

              </div>

            </div>

          )}

        </Tab>

        <Tab eventKey="second" title="Backlog 見た漢字">

          <Table striped bordered hover size="sm">
            <thead>
              <tr>
                <th width="170">Kanji</th>
                <th width="170">Meanings</th>
                <th width="170">Kun</th>
                <th width="870">On</th>
                <th width="1950">Previous review</th>
                <th width="1950">Next review</th>
              </tr>
            </thead>
            <tbody>
              {seenCards.map((seenCard) => (
                <tr key={seenCard.id}>
                  <td>{seenCard.kanji}</td>
                  <td>{seenCard.meanings}</td>
                  <td>{seenCard.readings_kun}</td>
                  <td>{seenCard.readings_on}</td>
                  <td>{seenCard.prev_review}</td>
                  <td>{seenCard.next_review}</td>
                </tr>
              ))}
            </tbody>
          </Table>

        </Tab>

        {/* Adding new cards */}
        <Tab eventKey="third" title="Add 新しい漢字">

        <div className='container'>
            <form onSubmit={handleFormSubmit}>

              <div className='mb-3 mt-3'>
                <label htmlFor='kanji' className='form-label'>
                  Kanji
                </label>
                <input type='text' className='form-control' id='kanji' name='kanji' onChange={handleInputChange} value={formData.kanji}/>
              </div>

              <div className='mb-3'>
                <label htmlFor='meanings' className='form-label'>
                  Meanings
                </label>
                <input type='text' className='form-control' id='meanings' name='meanings' onChange={handleInputChange} value={formData.meanings}/>
              </div>

              <div className='mb-3'>
                <label htmlFor='readings_kun' className='form-label'>
                  Kun readings
                </label>
                <input type='text' className='form-control' id='readings_kun' name='readings_kun' onChange={handleInputChange} value={formData.readings_kun}/>
              </div>

              <div className='mb-3'>
                <label htmlFor='readings_on' className='form-label'>
                  On readings
                </label>
                <input type='text' className='form-control' id='readings_on' name='readings_on' onChange={handleInputChange} value={formData.readings_on}/>
              </div>

              <button type='submit' className='btn btn-primary'>
                Add new card
              </button>

            </form>
          </div>

        </Tab>

      </Tabs>

    </div>
  );
}

export default App;

