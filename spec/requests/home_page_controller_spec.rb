require "rails_helper"

describe HomePageController, type: :request do
  let(:do_request) { get "/" }

  it "show a main page" do
    do_request
    expect(response).to have_http_status(:ok)
  end
end
