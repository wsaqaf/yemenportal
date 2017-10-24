RSpec.shared_examples "filter property" do
  context "when params aren't initialized with time" do
    let(:raw_params) { {} }

    it { is_expected.to eq(default_value) }
  end

  context "when params are initialized with filter property" do
    let(:raw_params) { { filter_property => property_value } }

    context "when property is initialized with predefined value" do
      let(:property_value) { valid_predefined_value }

      it { is_expected.to eq(property_value) }
    end

    context "when property is initialized with other value" do
      let(:property_value) { invalid_value }

      it { is_expected.to be_nil }
    end
  end
end
