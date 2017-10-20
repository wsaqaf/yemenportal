RSpec.shared_examples "votes including action" do
  it "includes user votes" do
    expect(Post).to receive(:include_voted_by_user).and_call_original
    do_request
  end
end
