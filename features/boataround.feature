Feature: testing boataround.com website

  Scenario: Visit bt2stag.boataround.com
    When Visit boataround website
    Then It should have an element with class "header__logo__img" and title "Boataround"
    And A pop-up ad message was displayed

  Scenario: Open search result page
    Given Enter a destination (Croatia), dates (check in: 01.06.2024, check out: 08.06.2024)
    When Visit search result page
    Then The search results page should display available boats for the specified dates

  Scenario: Open individual boat card
    Given Enter a destination (Croatia), dates (check in: 01.06.2024, check out: 08.06.2024)
    When Open second boat from list
    Then The product page should display available booking option for the specified dates

  Scenario: Change date on Availability calendar component
    When Choose first available option after selected dates
    Then The product page should have updated checkIn and checkOut params in url

  Scenario: Reserve option with the lowest price
    When Find lowest price around selected period
    And Click button "Reserve"
    Then "Enter your details" page should load without errors