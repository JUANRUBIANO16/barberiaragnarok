describe('Login', () => {

  it('login correcto', () => {

    cy.visit('/login');

    cy.get('#email').type('admin@correo.com');
    cy.get('#password').type('123456');

    cy.get('.login-btn').click();

    cy.url().should('not.include', '/login');
  });

});