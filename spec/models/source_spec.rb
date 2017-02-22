require "rails_helper"

describe Source do
  it { is_expected.to validate_presence_of(:link) }
end
