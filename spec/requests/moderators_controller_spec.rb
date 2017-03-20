require "rails_helper"

describe ModeratorsController, type: :request do
  let(:user) { create(:user, role: "moderator") }

  describe "#destroy" do
    let(:do_request) { delete "/moderators/#{user.id}", { "HTTP_REFERER" => "http://www.somewhere.net" } }

    xit "change moderator role" do
      do_request

      expect(response).to redirect_to(:back)
    end
  end

  describe "#index" do
    let(:do_request) { get "/moderators" }

    it "redirect to sources list" do
      sign_in user
      do_request

      expect(response.status).to eq 200
    end
  end
end
