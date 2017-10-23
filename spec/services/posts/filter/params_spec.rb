require "rails_helper"

describe Posts::Filter::Params do
  describe "#set" do
    subject { described_class.new(raw_params).set }

    let(:filter_property) { :set }
    let(:default_value) { :most_covered }
    let(:valid_predefined_value) { :highly_voted }
    let(:invalid_value) { :something }

    it_behaves_like "filter property"
  end

  describe "#time" do
    subject { described_class.new(raw_params).time }

    let(:filter_property) { :time }
    let(:default_value) { :daily }
    let(:valid_predefined_value) { :hourly }
    let(:invalid_value) { :something }

    it_behaves_like "filter property"
  end
end
