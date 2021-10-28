import React, {Component} from "react";
import { Link, withRouter } from "react-router-dom";
import 'bootstrap/dist/css/bootstrap.min.css';




class Navigation extends Component {

  constructor(props) {
    super(props);
    this.state = {
      menu: false
    };

    this.toggleMenu = this.toggleMenu.bind(this);
  }

  toggleMenu(){
    this.setState({ menu: !this.state.menu })
  }

 
  render()
  { const show = (this.state.menu) ? "show" : "" ;
  
  return(
    <div className="navigation" style={{padding:"0px 0px 10px 0px"}}>

    <nav className="navbar navbar-expand-lg navbar-dark bg-dark">
    
      <button className="navbar-toggler" type="button" onClick={ this.toggleMenu }>
        <span className="navbar-toggler-icon"></span>
      </button>
      <div className={"justify-content-end collapse navbar-collapse " + show}>
        <div className="navbar-nav">
        <ul className="navbar-nav">
              <li
                class={`nav-item  ${
                  this.props.location.pathname === "/" ? "active" : ""
                }`}
              >
                <Link class="nav-link nav-item" to="/">
                  Home
                  <span class="sr-only"></span>
                </Link>
              </li> 
              
              <li
                class={`nav-item  ${
                  this.props.location.pathname === "/Minter" ? "active" : ""
                }`}
              >
                <Link class="nav-link nav-item" to="/Minter">
                  Operator
                  <span class="sr-only"></span>
                </Link>
              </li> 

              <li
                class={`nav-item  ${
                  this.props.location.pathname === "/CrowdSale" ? "active" : ""
                }`}
              >
                <Link class="nav-link nav-item" to="/CrowdSale">
                  CrowdSale
                  <span class="sr-only"></span>
                </Link>
              </li> 

              <li
                class={`nav-item  ${
                  this.props.location.pathname === "/Register" ? "active" : ""
                }`}
              >
                <Link class="nav-link nav-item" to="/Register">
                  Register
                  <span class="sr-only"></span>
                </Link>
              </li> 

              <li
                class={`nav-item  ${
                  this.props.location.pathname === "/Exchange" ? "active" : ""
                }`}
              >
                <Link class="nav-link nav-item" to="/Exchange">
                  Exchange
                  <span class="sr-only"></span>
                </Link>
              </li>
            
            </ul>
        </div>
      </div>
    </nav>
          </div>
       
  
  )
}}

export default withRouter(Navigation);
