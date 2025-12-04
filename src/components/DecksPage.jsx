import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useDecks } from '../hooks/useDecks';
import Header from './Header';

const COLOR_CLASSES = {
  Red: 'color-red',
  Yellow: 'color-yellow', 
  Green: 'color-green',
  Blue: 'color-blue',
  Purple: 'color-purple',
  Colorless: 'color-gray'
};

export default function DecksPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { publicDecks, myDecks, loading, deleteDeck, toggleUpvote } = useDecks();
  const [tab, setTab] = useState('popular');
  const [colorFilter, setColorFilter] = useState('All');

  const handleDelete = async (deckId, deckName) => {
    if (confirm(`Delete "${deckName}"?`)) {
      await deleteDeck(deckId);
    }
  };

  const filteredDecks = (tab === 'mine' ? myDecks : publicDecks).filter(deck => {
    if (colorFilter === 'All') return true;
    return deck.colors?.includes(colorFilter);
  });

  const DeckCard = ({ deck, showActions }) => (
    <div className="deck-card">
      <Link to={`/deck/${deck.id}`} className="deck-card-link">
        <div className="deck-card-colors">
          {deck.colors?.map(c => (
            <span key={c} className={`color-dot ${COLOR_CLASSES[c] || ''}`} title={c} />
          ))}
        </div>
        <h3 className="deck-card-name">{deck.name}</h3>
        <div className="deck-card-meta">
          <span>by {deck.username}</span>
          <span>{deck.cards?.reduce((s, c) => s + c.quantity, 0) || 0} cards</span>
        </div>
      </Link>
      <div className="deck-card-footer">
        <button 
          className={`upvote-btn ${deck.upvotedBy?.includes(user?.uid) ? 'upvoted' : ''}`}
          onClick={() => toggleUpvote(deck.id)}
          disabled={!user}
        >
          ▲ {deck.upvotes || 0}
        </button>
        {showActions && (
          <div className="deck-card-actions">
            <button onClick={() => navigate(`/builder/${deck.id}`)}>Edit</button>
            <button onClick={() => handleDelete(deck.id, deck.name)}>Delete</button>
          </div>
        )}
      </div>
    </div>
  );

  return (
    <div className="app">
      <Header />
      <div className="decks-page">
        <div className="decks-header">
          <h1>Decks</h1>
          <button onClick={() => navigate('/builder')} className="new-deck-btn">
            + New Deck
          </button>
        </div>

        <div className="decks-tabs">
          <button className={tab === 'popular' ? 'active' : ''} onClick={() => setTab('popular')}>
            Popular
          </button>
          {user && (
            <button className={tab === 'mine' ? 'active' : ''} onClick={() => setTab('mine')}>
              My Decks ({myDecks.length})
            </button>
          )}
          <select 
            value={colorFilter} 
            onChange={(e) => setColorFilter(e.target.value)}
            className="color-filter-select"
          >
            <option value="All">All Colors</option>
            <option value="Red">Red</option>
            <option value="Yellow">Yellow</option>
            <option value="Green">Green</option>
            <option value="Blue">Blue</option>
            <option value="Purple">Purple</option>
          </select>
        </div>

        {loading ? (
          <div className="loading">Loading decks...</div>
        ) : filteredDecks.length === 0 ? (
          <div className="no-decks">
            {tab === 'mine' ? 'You haven\'t created any decks yet.' : 'No decks found.'}
          </div>
        ) : (
          <div className="decks-grid">
            {filteredDecks.map(deck => (
              <DeckCard key={deck.id} deck={deck} showActions={tab === 'mine'} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
