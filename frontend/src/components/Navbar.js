import React from 'react';
import { Link } from 'react-router-dom';

const Navbar = () => {
  return (
    <nav className="navbar navbar-expand-lg navbar-dark" style={{ backgroundColor: "#000000", boxShadow: "0 2px 5px rgba(0,0,0,0.2)" }}>
      <div className="container">
        <Link className="navbar-brand" to="/">
          <i className="fas fa-search-dollar me-2"></i>
        </Link>
        <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
          <span className="navbar-toggler-icon"></span>
        </button>
        <div className="collapse navbar-collapse" id="navbarNav">
          <ul className="navbar-nav ms-auto">
            <li className="nav-item">
              <Link className="nav-link active" to="/">
                <i className="fas fa-home me-1"></i> Trang chủ
              </Link>
            </li>
            <li className="nav-item">
              <a className="nav-link" href="#about">
                <i className="fas fa-info-circle me-1"></i> Giới thiệu
              </a>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  );
};

export default Navbar; 