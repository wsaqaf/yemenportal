describe ApplicationPolicy do
  subject { described_class }

  describe "#admin" do
    permissions :admin? do
      it "access if user has role admin" do
        expect(subject).to permit(User.new(role: :admin))
      end

      it "denies access if user has role moderator" do
        expect(subject).not_to permit(User.new(role: :moderator))
      end

      it "denies access if user has role member" do
        expect(subject).not_to permit(User.new(role: :member))
      end
    end
  end

  describe "#moderator" do
    permissions :moderator? do
      it "access if user has role admin" do
        expect(subject).to permit(User.new(role: :admin))
      end

      it "access if user has role moderator" do
        expect(subject).to permit(User.new(role: :moderator))
      end

      it "denies access if user has role member" do
        expect(subject).not_to permit(User.new(role: :member))
      end
    end
  end
end
