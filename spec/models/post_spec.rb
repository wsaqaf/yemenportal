require "rails_helper"

describe Post do
  %i(title published_at link).each do |field|
    it { is_expected.to validate_presence_of(field) }
  end
end
