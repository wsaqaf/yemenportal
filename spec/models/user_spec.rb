require "rails_helper"

describe User do
  %i(email role).each do |field|
    it { is_expected.to validate_presence_of(field) }
  end

  it { is_expected.to validate_uniqueness_of(:email) }
end
