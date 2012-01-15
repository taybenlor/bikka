require 'watir-webdriver'
require 'rspec/expectations'
require 'sqlite3'

Given /^I am logged in as "([^"]*)"$/ do |username|
  db = SQLite3::Database.new '../../database.sqlitedb' 
  rows = db.execute "select * from users where username = '#{username}'"
  if !rows.length
    db.execute "insert into users ('username', 'password') values ('test_bob', 'test_bob')"
  end

  When "I go to the login page"
  And "I log in as \"test_bob\" with password \"test_bob\""
end
