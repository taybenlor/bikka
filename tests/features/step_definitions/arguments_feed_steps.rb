require 'watir-webdriver'
require 'rspec/expectations'
require 'sqlite3'

Given /^I am on the homepage$/ do
  @browser ||= Watir::Browser.new :ff
  @browser.goto "http://localhost:8888"
end

Then /^I should see "([^"]*)"$/ do |text|
  @browser.text.include?(text).should be_true
end

Given /^I go to the create argument page$/ do
  @browser.goto "http://localhost:8888/argument/create"
end

And /^an argument exists$/ do
  db = SQLite3::Database.new 'database.sqlitedb'
  db.execute "insert into posts (title, description, time, user_id) values ('test_awesome_title', 'test_awesome_desc', datetime(), 0)"
end

After do
  @browser.close
end
