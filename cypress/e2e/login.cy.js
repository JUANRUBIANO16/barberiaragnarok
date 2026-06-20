describe('Login sistema', () => {

  it('login correcto', () => {

    cy.visit('https://barberiaragnarok.onrender.com/');

    cy.get('#email').type('admin@gmail.com');
    cy.get('#password').type('admin123');

    cy.get('.login-btn').click();

    // espera redirección real
    cy.url().should('include', '/dashboard/');

    // valida que entró al sistema
    cy.contains('Bienvenido');
  });

});K