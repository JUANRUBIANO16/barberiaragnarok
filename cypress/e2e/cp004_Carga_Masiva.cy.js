describe('CP-004 - Carga masiva de usuarios', () => {

  it('Debe permitir importar usuarios desde Excel correctamente', () => {

    // =========================
    // 1. LOGIN (REUTILIZABLE)
    // =========================
    cy.login();

    // =========================
    // 2. IR A USUARIOS
    // =========================
    cy.visit('https://barberiaragnarok.onrender.com/usuarios/');

    // =========================
    // 3. ABRIR MODAL
    // =========================
    cy.contains('Importar Excel')
      .click({ force: true });

    cy.get('#uploadExcelModal')
      .should('be.visible');

    // =========================
    // 4. SUBIR EXCEL
    // =========================
    cy.get('#uploadExcelModal')
      .find('input[name="archivo"]')
      .selectFile('cypress/fixtures/usuarios_prueba.xlsx', {
        force: true
      });

    // =========================
    // 5. CONFIRMAR CARGA
    // =========================
    cy.contains('Importar')
      .click({ force: true });

    // =========================
    // 6. VALIDACIÓN REAL
    // =========================

    // Espera a que procese el backend
    cy.wait(2000);

    // ✔ Validar que la tabla tenga datos (PRUEBA REAL)
    cy.get('table')
      .should('exist')
      .and('contain', 'juan');

  });

});