require "rails_helper"

describe Posts::Filter::Params do
  describe "#set" do
    subject { described_class.new(raw_params).set }

    context "when params aren't initialized with set" do
      let(:raw_params) { {} }

      it { is_expected.to eq(:most_covered) }
    end

    context "when params are initialized with set" do
      let(:raw_params) { { set: set_value } }

      context "when set is initialized with predefined value" do
        let(:set_value) { :highly_voted }

        it { is_expected.to eq(set_value) }
      end

      context "when set is initialized with other value" do
        let(:set_value) { :something }

        it { is_expected.to be_nil }
      end
    end
  end
end
